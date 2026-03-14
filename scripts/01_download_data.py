"""Download all datasets needed for the Autobahn speed-safety analysis.

Run from project root:
    uv run python scripts/01_download_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autobahn_safety.data_loaders import (
    download_bron,
    download_destatis_timeseries,
    download_unfallatlas,
    fetch_cbs_odata,
    load_bron,
    load_destatis_autobahn,
    load_unfallatlas,
)

DATA_RAW = Path("data/raw")
DATA_RAW.mkdir(parents=True, exist_ok=True)

# ── 1. Germany — Unfallatlas ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print("1. Unfallatlas (Germany GPS accident records 2016–2024)")
print("=" * 60)

UNFALLATLAS_DIR = DATA_RAW / "germany" / "unfallatlas"
YEARS_DE = list(range(2016, 2025))

for year in YEARS_DE:
    year_dir = UNFALLATLAS_DIR / str(year)
    try:
        download_unfallatlas(year, year_dir)
    except Exception as e:
        print(f"  {year}: FAILED — {e}")

df_unfallatlas = load_unfallatlas(UNFALLATLAS_DIR, YEARS_DE)
print(f"  Loaded {len(df_unfallatlas):,} records, years {sorted(df_unfallatlas['year'].unique().tolist())}")

# ── 2. Germany — Destatis timeseries ─────────────────────────────────────────
print("\n" + "=" * 60)
print("2. Destatis accident timeseries (1979–2021)")
print("=" * 60)

DESTATIS_DIR = DATA_RAW / "germany" / "destatis"
DESTATIS_DIR.mkdir(parents=True, exist_ok=True)

xlsx_path = download_destatis_timeseries(DESTATIS_DIR)
df_autobahn = load_destatis_autobahn(xlsx_path)
print(f"  {len(df_autobahn)} years ({df_autobahn['year'].min()}–{df_autobahn['year'].max()})")

# ── 3. Netherlands — CBS OData ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. CBS OData (deaths + vehicle-km)")
print("=" * 60)

CBS_DIR = DATA_RAW / "netherlands" / "cbs"
CBS_DIR.mkdir(parents=True, exist_ok=True)

for ds_id, name in [("71426ned", "deaths_by_province"), ("71936ned", "deaths_by_mode")]:
    out = CBS_DIR / f"{name}.csv"
    if out.exists():
        print(f"  {ds_id} ({name}): already cached")
        continue
    df = fetch_cbs_odata(ds_id)
    df.to_csv(out, index=False)
    print(f"  {ds_id}: {len(df):,} rows saved")

out_vkm = CBS_DIR / "vehicle_km_by_type.csv"
if not out_vkm.exists():
    import pandas as pd
    df_vkm = fetch_cbs_odata("85395NED")
    df_vkm.to_csv(out_vkm, index=False)
    print(f"  85395NED: {len(df_vkm):,} rows saved (vehicle-km)")
else:
    print("  85395NED (vehicle-km): already cached")

# ── 4. Netherlands — BRON ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. BRON (NL GPS accident records 2010–2024)")
print("=" * 60)

BRON_DIR = DATA_RAW / "netherlands" / "bron"
BRON_DIR.mkdir(parents=True, exist_ok=True)

for year in range(2010, 2025):
    try:
        download_bron(year=year, output_dir=BRON_DIR)
    except Exception as e:
        print(f"  {year}: FAILED — {e}")

bron_years = sorted([int(f.stem.split("_")[-1]) for f in BRON_DIR.glob("bron_accidents_*.csv")])
if bron_years:
    df_bron = load_bron(BRON_DIR, bron_years[-1:])
    print(f"  Latest year ({bron_years[-1]}): {len(df_bron):,} records")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Unfallatlas : {len(df_unfallatlas):,} records ({YEARS_DE[0]}–{YEARS_DE[-1]})")
print(f"  Destatis    : {len(df_autobahn)} years ({df_autobahn['year'].min()}–{df_autobahn['year'].max()})")

import pandas as pd
for name in ["deaths_by_province", "deaths_by_mode", "vehicle_km_by_type"]:
    p = CBS_DIR / f"{name}.csv"
    if p.exists():
        print(f"  CBS {name}: {len(pd.read_csv(p, low_memory=False)):,} rows")

if bron_years:
    total = sum(
        len(pd.read_csv(BRON_DIR / f"bron_accidents_{y}.csv", dtype=str, low_memory=False))
        for y in bron_years
    )
    print(f"  BRON        : {total:,} records ({bron_years[0]}–{bron_years[-1]})")

print("\nDownload complete.")
