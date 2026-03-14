"""Process all datasets for the Autobahn speed-safety analysis.

Produces:
  data/processed/unfallatlas_classified.parquet  — DE accidents with motorway/unlimited flags
  data/processed/rws_motorway_annual.parquet     — NL motorway annual summary

Run from project root:
    uv run python scripts/02_process_data.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autobahn_safety.data_loaders import load_bron, load_unfallatlas
from autobahn_safety.preprocessing import clean_unfallatlas

DATA_RAW = Path("data/raw")
DATA_PROC = Path("data/processed")
DATA_PROC.mkdir(parents=True, exist_ok=True)

# ── 1. Load and clean Unfallatlas ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("1. Loading Unfallatlas")
print("=" * 60)

df_ua = load_unfallatlas(DATA_RAW / "germany" / "unfallatlas", list(range(2016, 2025)))
df_ua = clean_unfallatlas(df_ua)
print(f"  {len(df_ua):,} records, {df_ua['year'].nunique()} years")

# ── 2. Download / load OSM motorway network ───────────────────────────────────
print("\n" + "=" * 60)
print("2. German Autobahn network (OSM)")
print("=" * 60)

MOTORWAY_CACHE = DATA_PROC / "germany_motorways.gpkg"

if MOTORWAY_CACHE.exists():
    print("  Loading cached motorway network...")
    gdf_motorways = gpd.read_file(MOTORWAY_CACHE)
    print(f"  {len(gdf_motorways):,} motorway segments loaded")
else:
    print("  Downloading German Autobahn network from OSM by Bundesland...")
    # Download state-by-state to avoid Overpass timeout on a single Germany query
    BUNDESLAENDER = [
        "Baden-Württemberg, Germany", "Bayern, Germany", "Berlin, Germany",
        "Brandenburg, Germany", "Bremen, Germany", "Hamburg, Germany",
        "Hessen, Germany", "Mecklenburg-Vorpommern, Germany",
        "Niedersachsen, Germany", "Nordrhein-Westfalen, Germany",
        "Rheinland-Pfalz, Germany", "Saarland, Germany",
        "Sachsen, Germany", "Sachsen-Anhalt, Germany",
        "Schleswig-Holstein, Germany", "Thüringen, Germany",
    ]
    frames = []
    for state in BUNDESLAENDER:
        try:
            G = ox.graph_from_place(
                state,
                network_type="drive",
                custom_filter='["highway"~"motorway|motorway_link"]',
                retain_all=False,
            )
            _, edges = ox.graph_to_gdfs(G)
            keep = [c for c in ["geometry", "highway", "maxspeed", "name", "ref"] if c in edges.columns]
            frames.append(edges[keep].copy())
            print(f"    {state.split(',')[0]}: {len(edges):,} segments")
        except Exception as e:
            print(f"    {state.split(',')[0]}: FAILED — {e}")

    gdf_motorways = pd.concat(frames, ignore_index=True)
    gdf_motorways = gdf_motorways.drop_duplicates(subset=["geometry"]).reset_index(drop=True)
    gdf_motorways.to_file(MOTORWAY_CACHE, driver="GPKG")
    print(f"  Downloaded and cached {len(gdf_motorways):,} total segments")

# ── 3. Classify speed limit sections ─────────────────────────────────────────
print("\n" + "=" * 60)
print("3. Classifying Autobahn speed-limit sections")
print("=" * 60)


def is_unlimited(maxspeed: object) -> bool:
    """Return True if the section has no effective speed limit."""
    if isinstance(maxspeed, list):
        return all(is_unlimited(v) for v in maxspeed)
    if pd.isna(maxspeed):
        return True
    ms = str(maxspeed).lower().strip()
    return ms in ("", "de:motorway", "de", "none", "signals")


gdf_motorways["unlimited"] = gdf_motorways["maxspeed"].apply(is_unlimited)
n_unl = gdf_motorways["unlimited"].sum()
n_lim = (~gdf_motorways["unlimited"]).sum()
print(f"  Unlimited sections : {n_unl:,} ({n_unl/(n_unl+n_lim)*100:.1f}%)")
print(f"  Speed-limited      : {n_lim:,} ({n_lim/(n_unl+n_lim)*100:.1f}%)")

# ── 4. Spatial join: tag each accident as motorway/non-motorway ───────────────
print("\n" + "=" * 60)
print("4. Spatial join (accident points ↔ Autobahn network)")
print("=" * 60)

df_clean = df_ua.dropna(subset=["lon", "lat"])
gdf_acc = gpd.GeoDataFrame(
    df_clean,
    geometry=gpd.points_from_xy(df_clean["lon"], df_clean["lat"]),
    crs="EPSG:4326",
)
gdf_acc = gdf_acc.to_crs("EPSG:25832")
gdf_mw = gdf_motorways.to_crs("EPSG:25832")

print("  Buffering motorway network (50m)...")
gdf_mw_buf = gdf_mw.copy()
gdf_mw_buf["geometry"] = gdf_mw_buf.geometry.buffer(50)

print("  Running spatial join...")
joined = gpd.sjoin(gdf_acc, gdf_mw_buf[["geometry", "unlimited"]], how="left", predicate="within")
joined = joined[~joined.index.duplicated(keep="first")]

df_ua["on_motorway"] = (~joined["unlimited"].isna()).astype(bool)
df_ua["on_unlimited"] = joined["unlimited"].fillna(False).astype(bool)
df_ua["on_limited_mw"] = (df_ua["on_motorway"] & ~df_ua["on_unlimited"]).astype(bool)

for col, label in [
    ("on_motorway", "Motorway total"),
    ("on_unlimited", "  ↳ unlimited"),
    ("on_limited_mw", "  ↳ limited   "),
]:
    n, pct = df_ua[col].sum(), df_ua[col].mean() * 100
    print(f"  {label}: {n:,} ({pct:.1f}%)")

out_ua = DATA_PROC / "unfallatlas_classified.parquet"
pq.write_table(pa.Table.from_pandas(df_ua, preserve_index=False), out_ua)
print(f"  Saved → {out_ua}")

# ── 5. Netherlands — classify and aggregate BRON data ─────────────────────────
print("\n" + "=" * 60)
print("5. Processing BRON (Netherlands)")
print("=" * 60)

BRON_DIR = DATA_RAW / "netherlands" / "bron"
bron_years = sorted([int(f.stem.split("_")[-1]) for f in BRON_DIR.glob("bron_accidents_*.csv")])

if not bron_years:
    print("  No BRON data found — run 01_download_data.py first")
else:
    print(f"  Loading {len(bron_years)} years: {bron_years}")
    df_rws = load_bron(BRON_DIR, bron_years)
    df_rws["year"] = df_rws["JAAR_VKL"].astype(int)
    df_rws["MAXSNELHD_num"] = pd.to_numeric(df_rws["MAXSNELHD"], errors="coerce")

    def classify_road_nl(row: pd.Series) -> str:
        spd = row["MAXSNELHD_num"]
        bebkom = row.get("BEBKOM", "")
        if pd.isna(spd):
            return "unknown"
        spd = int(spd)
        if spd in (100, 120, 130):
            return "motorway"
        elif spd in (60, 70, 80, 90) and bebkom == "BU":
            return "n_road"
        elif spd == 50:
            return "urban_50"
        elif spd == 30:
            return "urban_30"
        return "other"

    df_rws["road_type"] = df_rws.apply(classify_road_nl, axis=1)
    df_mw_nl = df_rws[df_rws["road_type"] == "motorway"].copy()
    print(f"  {len(df_rws):,} total records, {len(df_mw_nl):,} motorway")

    annual_nl = (
        df_mw_nl.groupby("year")
        .agg(
            total=("AP3_CODE", "count"),
            fatal=("AP3_CODE", lambda x: (x == "DOD").sum()),
            serious=("AP3_CODE", lambda x: (x == "ZGO").sum()),
            slight=("AP3_CODE", lambda x: (x == "LOO").sum()),
            material=("AP3_CODE", lambda x: (x == "UMS").sum()),
        )
        .reset_index()
    )
    annual_nl["severity_idx"] = annual_nl["fatal"] / annual_nl["total"]

    out_nl = DATA_PROC / "rws_motorway_annual.parquet"
    annual_nl.to_parquet(out_nl, index=False)
    print(f"  Saved → {out_nl}")
    print(f"\n  NL motorway annual summary:")
    print(annual_nl.to_string(index=False))

print("\nProcessing complete.")
