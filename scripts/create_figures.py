"""Generate all analysis figures (fig01–fig12) for the Autobahn speed-safety analysis.

Loads processed data from data/processed/ and saves figures to output/figures/.
Mirrors the logic in notebooks 03–06 and consolidates scripts/03_create_plots.py.

Usage (from project root):
    .venv/bin/python scripts/create_figures.py                   # all figures
    .venv/bin/python scripts/create_figures.py --figures 7 8 9   # subset
    .venv/bin/python scripts/create_figures.py --figures 10 11 12 # hypothesis tests
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from scipy import stats

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autobahn_safety.data_loaders import load_destatis_autobahn

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
FIG_DIR = ROOT / "output" / "figures"

# ── Constants ──────────────────────────────────────────────────────────────────
KM_DE_UNLIMITED = 16_441   # km of unlimited-speed Autobahn (OSM, pre-computed)
KM_DE_LIMITED   = 10_618   # km of speed-limited Autobahn
KM_NL           = 2_758    # km of Dutch autosnelwegen (RWS standard figure)

PALETTE = {
    "DE: Unlimited Autobahn": "#e63946",
    "DE: Limited Autobahn":   "#457b9d",
    "NL: Motorway":           "#2a9d8f",
}


# ── Helpers ────────────────────────────────────────────────────────────────────
def _save(fig: plt.Figure, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.close(fig)


# ── Data loaders (lazy, cached in module-level dict) ──────────────────────────
_cache: dict[str, object] = {}


def _load_ua() -> pd.DataFrame:
    if "ua" not in _cache:
        path = DATA_PROC / "unfallatlas_classified.parquet"
        if not path.exists():
            raise FileNotFoundError(
                f"Unfallatlas parquet not found: {path}\n"
                "Run notebook 03 or scripts/02_process_data.py first."
            )
        _cache["ua"] = pd.read_parquet(path)
        print(f"  Loaded Germany: {len(_cache['ua']):,} accident records")
    return _cache["ua"]  # type: ignore[return-value]


def _load_nl() -> pd.DataFrame:
    if "nl" not in _cache:
        path = DATA_PROC / "rws_motorway_annual.parquet"
        if not path.exists():
            raise FileNotFoundError(
                f"NL annual parquet not found: {path}\n"
                "Run notebook 04 or scripts/02_process_data.py first."
            )
        _cache["nl"] = pd.read_parquet(path)
        print(f"  Loaded Netherlands: {len(_cache['nl'])} years")
    return _cache["nl"]  # type: ignore[return-value]


def _load_destatis() -> pd.DataFrame:
    if "destatis" not in _cache:
        path = DATA_RAW / "germany" / "destatis" / "destatis_verkehrsunfaelle_zeitreihen.xlsx"
        if not path.exists():
            raise FileNotFoundError(
                f"Destatis Excel not found: {path}\n"
                "Run notebook 01 or scripts/01_download_data.py first."
            )
        _cache["destatis"] = load_destatis_autobahn(path)
        print(f"  Loaded Destatis: {len(_cache['destatis'])} years")
    return _cache["destatis"]  # type: ignore[return-value]


def _de_annual(df_ua: pd.DataFrame) -> pd.DataFrame:
    """Build per-year summary for DE unlimited and limited Autobahn."""
    groups = {
        "DE: Unlimited Autobahn": df_ua[df_ua["on_unlimited"]],
        "DE: Limited Autobahn":   df_ua[df_ua["on_limited_mw"]],
    }
    frames = []
    for label, grp in groups.items():
        by_year = (
            grp.groupby("year")
            .agg(
                total=("severity", "count"),
                fatal=("severity", lambda x: (x == "fatal").sum()),
                serious=("severity", lambda x: (x == "serious_injury").sum()),
            )
            .reset_index()
        )
        by_year["group"] = label
        by_year["severity_idx"] = by_year["fatal"] / by_year["total"]
        frames.append(by_year)
    return pd.concat(frames, ignore_index=True)


# ── Figure functions ───────────────────────────────────────────────────────────

def fig01() -> None:
    """Long-term DE Autobahn trend (Destatis)."""
    print("Fig 01: Long-term Autobahn trend (Destatis)")
    df = _load_destatis()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].plot(df["year"], df["accidents_personal_injury"],
                 color="steelblue", linewidth=2)
    axes[0].fill_between(df["year"], df["accidents_personal_injury"],
                         alpha=0.15, color="steelblue")
    axes[0].set_title("Personal-injury accidents")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Accidents")

    axes[1].plot(df["year"], df["accidents_fatal"],
                 color="crimson", linewidth=2)
    axes[1].fill_between(df["year"], df["accidents_fatal"],
                         alpha=0.15, color="crimson")
    axes[1].set_title("Fatal accidents")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Fatal accidents")

    fig.suptitle("German Autobahn: long-term safety trend (Destatis)",
                 fontweight="bold", fontsize=13)
    plt.tight_layout()
    _save(fig, "fig01_destatis_longterm")


def fig02() -> None:
    """Severity index by road type (Germany, Unfallatlas)."""
    print("Fig 02: DE severity index by road type")
    df_ua = _load_ua()

    all_groups = {
        "Unlimited Autobahn":    df_ua[df_ua["on_unlimited"]],
        "Speed-limited Autobahn": df_ua[df_ua["on_limited_mw"]],
        "Non-motorway":          df_ua[~df_ua["on_motorway"]],
    }
    colors_de = {
        "Unlimited Autobahn":    "#e63946",
        "Speed-limited Autobahn": "#457b9d",
        "Non-motorway":          "#adb5bd",
    }

    fig, ax = plt.subplots(figsize=(11, 5))
    for label, grp in all_groups.items():
        by_year = (
            grp.groupby("year")
            .agg(total=("severity", "count"),
                 fatal=("severity", lambda x: (x == "fatal").sum()))
            .reset_index()
        )
        by_year["severity_idx"] = by_year["fatal"] / by_year["total"]
        ax.plot(by_year["year"], by_year["severity_idx"] * 1000,
                marker="o", label=label, linewidth=2, color=colors_de[label])

    ax.set_title("Germany: severity index by road type (fatalities per 1000 accidents)",
                 fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Fatalities per 1000 accidents")
    ax.legend()
    plt.tight_layout()
    _save(fig, "fig02_de_severity_by_roadtype")


def fig03() -> None:
    """NL motorway annual safety trends."""
    print("Fig 03: NL motorway annual trends")
    df_nl = _load_nl()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].plot(df_nl["year"], df_nl["total"],
                 marker="o", color="#2a9d8f", linewidth=2, label="Total")
    axes[0].plot(df_nl["year"], df_nl["serious"],
                 marker="s", color="#e9c46a", linewidth=2, label="Serious injury")
    axes[0].plot(df_nl["year"], df_nl["fatal"],
                 marker="^", color="crimson", linewidth=2, label="Fatal")
    axes[0].set_title("Motorway accidents by severity")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Count")
    axes[0].legend()

    axes[1].plot(df_nl["year"], df_nl["severity_idx"] * 1000,
                 marker="o", color="crimson", linewidth=2)
    axes[1].set_title("Severity index (fatalities per 1000 accidents)")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Fatalities per 1000 accidents")

    fig.suptitle("Netherlands motorway safety (BRON)", fontweight="bold", fontsize=13)
    plt.tight_layout()
    _save(fig, "fig03_nl_motorway_trends")


def fig04() -> None:
    """DE vs NL severity index comparison."""
    print("Fig 04: DE vs NL severity index comparison")
    df_ua = _load_ua()
    df_nl = _load_nl()

    df_de_ann = _de_annual(df_ua)
    df_nl_plot = df_nl[["year", "total", "fatal", "severity_idx"]].copy()
    df_nl_plot["group"] = "NL: Motorway"
    df_combined = pd.concat([df_de_ann, df_nl_plot], ignore_index=True)

    fig, ax = plt.subplots(figsize=(11, 5))
    for grp_name, grp in df_combined.groupby("group"):
        ax.plot(grp["year"], grp["severity_idx"] * 1000,
                marker="o", label=grp_name, linewidth=2,
                color=PALETTE.get(grp_name, "grey"))

    ax.set_title("Severity index: fatalities per 1000 accidents — DE vs NL",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Fatalities per 1000 accidents")
    ax.legend()
    plt.tight_layout()
    _save(fig, "fig04_de_vs_nl_severity_index")


def fig05() -> None:
    """Summary bar chart: mean fatality rate comparison."""
    print("Fig 05: Summary bar chart")
    df_ua = _load_ua()
    df_nl = _load_nl()

    common_years = set(df_ua["year"].unique()) & set(df_nl["year"].unique())
    means = {
        "DE: Unlimited\nAutobahn": (
            df_ua[df_ua["on_unlimited"] & df_ua["year"].isin(common_years)]["severity"] == "fatal"
        ).mean() * 1000,
        "DE: Limited\nAutobahn": (
            df_ua[df_ua["on_limited_mw"] & df_ua["year"].isin(common_years)]["severity"] == "fatal"
        ).mean() * 1000,
        "NL:\nMotorway": df_nl[df_nl["year"].isin(common_years)]["severity_idx"].mean() * 1000,
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(list(means.keys()), list(means.values()),
                  color=["#e63946", "#457b9d", "#2a9d8f"],
                  width=0.5, edgecolor="white")
    ax.bar_label(bars, fmt="%.2f", padding=4, fontsize=12, fontweight="bold")
    ax.set_title(
        f"Mean fatality rate comparison (per 1000 accidents)\n"
        f"Common years: {min(common_years)}–{max(common_years)}",
        fontsize=13, fontweight="bold",
    )
    ax.set_ylabel("Fatalities per 1000 accidents")
    ax.set_ylim(0, max(means.values()) * 1.35)
    sns.despine()
    plt.tight_layout()
    _save(fig, "fig05_summary_bar")


def fig06() -> None:
    """Annual rate ratio: unlimited vs limited Autobahn."""
    print("Fig 06: Annual rate ratio unlimited vs limited")
    df_ua = _load_ua()

    years = sorted(df_ua["year"].unique())
    results = []
    for yr in years:
        yr_data = df_ua[df_ua["year"] == yr]
        n_unl    = int((yr_data["on_unlimited"]  & (yr_data["severity"] == "fatal")).sum())
        n_lim    = int((yr_data["on_limited_mw"] & (yr_data["severity"] == "fatal")).sum())
        tot_unl  = int(yr_data["on_unlimited"].sum())
        tot_lim  = int(yr_data["on_limited_mw"].sum())
        if tot_unl > 0 and tot_lim > 0 and n_lim > 0:
            results.append({
                "year":           yr,
                "rate_unlimited": n_unl / tot_unl * 1000,
                "rate_limited":   n_lim / tot_lim * 1000,
                "rate_ratio":     (n_unl / tot_unl) / (n_lim / tot_lim),
            })
    df_res = pd.DataFrame(results)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].plot(df_res["year"], df_res["rate_unlimited"],
                 marker="o", color="#e63946", linewidth=2, label="Unlimited")
    axes[0].plot(df_res["year"], df_res["rate_limited"],
                 marker="s", color="#457b9d", linewidth=2, label="Speed-limited")
    axes[0].set_title("Fatality rate: unlimited vs limited Autobahn")
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Fatalities per 1000 accidents")
    axes[0].legend()

    axes[1].bar(df_res["year"], df_res["rate_ratio"], color="#f4a261")
    axes[1].axhline(1.0, color="grey", linestyle="--", linewidth=1)
    axes[1].set_title("Rate ratio (unlimited / limited)")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Rate ratio")

    fig.suptitle("Unlimited vs speed-limited Autobahn: fatality rate comparison",
                 fontweight="bold", fontsize=13)
    plt.tight_layout()
    _save(fig, "fig06_rate_ratio_unlimited_vs_limited")


def fig07() -> None:
    """Motorway fatalities per million inhabitants per year (DE vs NL)."""
    print("Fig 07: Motorway fatalities per million inhabitants per year")

    # Population constants (source: Germany 2020 census average; Netherlands 2020 CBS average)
    POP_DE_M = 83.2   # Germany population in millions
    POP_NL_M = 17.6   # Netherlands population in millions

    # Germany: Destatis Autobahn fatal accidents (whole network)
    df_de = _load_destatis()
    de_data = df_de[df_de["year"].between(2016, 2021)][["year", "accidents_fatal"]].copy()
    de_data["deaths_per_mio"] = de_data["accidents_fatal"] / POP_DE_M

    # Netherlands: CBS deaths by transport mode
    # Filter: Geslacht=='T001038' (total), Leeftijd==10000 (all ages),
    #         WijzeVanDeelname=='A048748' (motorway)
    cbs_path = DATA_RAW / "netherlands" / "cbs" / "deaths_by_mode.csv"
    if not cbs_path.exists():
        raise FileNotFoundError(f"CBS deaths file not found: {cbs_path}")
    df_cbs = pd.read_csv(cbs_path, sep=",")
    df_cbs["year"] = df_cbs["Perioden"].str[:4].astype(int)
    nl_raw = df_cbs[
        (df_cbs["Geslacht"].str.strip() == "T001038")
        & (df_cbs["Leeftijd"] == 10000)
        & (df_cbs["WijzeVanDeelname"].str.strip() == "A048748")
    ].copy()
    nl_data = nl_raw[nl_raw["year"].between(2016, 2021)][["year", "Verkeersdoden_1"]].copy()
    nl_data = nl_data.rename(columns={"Verkeersdoden_1": "deaths"})
    nl_data["deaths_per_mio"] = nl_data["deaths"] / POP_NL_M

    # Print summary table
    print(f"\n  {'Year':>6}  {'DE deaths':>10}  {'DE/mio':>8}  {'NL deaths':>10}  {'NL/mio':>8}")
    print("  " + "-" * 52)
    merged = de_data.merge(nl_data, on="year", suffixes=("_de", "_nl"))
    for _, row in merged.iterrows():
        print(f"  {int(row['year']):>6}  {int(row['accidents_fatal']):>10}  "
              f"{row['deaths_per_mio_de']:>8.2f}  "
              f"{int(row['deaths']):>10}  {row['deaths_per_mio_nl']:>8.2f}")
    print()

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(de_data["year"], de_data["deaths_per_mio"],
            marker="s", color="#e63946", linewidth=2.5, label="Germany (Autobahn)")
    ax.plot(nl_data["year"], nl_data["deaths_per_mio"],
            marker="o", color="#2a9d8f", linewidth=2.5, label="Netherlands (motorway)")

    # Annotate points
    for _, row in de_data.iterrows():
        ax.annotate(f"{row['deaths_per_mio']:.1f}",
                    xy=(row["year"], row["deaths_per_mio"]),
                    xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=9, color="#e63946")
    for _, row in nl_data.iterrows():
        ax.annotate(f"{row['deaths_per_mio']:.1f}",
                    xy=(row["year"], row["deaths_per_mio"]),
                    xytext=(0, -16), textcoords="offset points",
                    ha="center", fontsize=9, color="#2a9d8f")

    ax.set_title("Motorway fatalities per million inhabitants: Germany vs Netherlands",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Motorway deaths per million inhabitants")
    ax.set_xticks(sorted(merged["year"].unique()))
    ax.legend(fontsize=11)
    ax.set_ylim(bottom=0)
    sns.despine()
    plt.tight_layout()
    _save(fig, "fig07_motorway_deaths_per_capita")


def fig08() -> None:
    """Accident density — all accidents and fatal accidents per 100 km (Germany only)."""
    print("Fig 08: Accident density — all accidents per 100 km (DE only)")
    df_ua = _load_ua()

    de_mw = df_ua[df_ua["on_motorway"]]
    de_unl_all = de_mw[de_mw["on_unlimited"]].groupby("year").size().rename("total_unl")
    de_lim_all = de_mw[de_mw["on_limited_mw"]].groupby("year").size().rename("total_lim")
    de_unl_fat = (
        de_mw[de_mw["on_unlimited"] & (de_mw["severity"] == "fatal")]
        .groupby("year").size().rename("fatal_unl")
    )
    de_lim_fat = (
        de_mw[de_mw["on_limited_mw"] & (de_mw["severity"] == "fatal")]
        .groupby("year").size().rename("fatal_lim")
    )
    df8 = pd.concat([de_unl_all, de_lim_all, de_unl_fat, de_lim_fat], axis=1).reset_index()
    df8["total_density_unl"] = df8["total_unl"] / KM_DE_UNLIMITED * 100
    df8["total_density_lim"] = df8["total_lim"] / KM_DE_LIMITED   * 100
    df8["fatal_density_unl"] = df8["fatal_unl"] / KM_DE_UNLIMITED * 100
    df8["fatal_density_lim"] = df8["fatal_lim"] / KM_DE_LIMITED   * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

    ax = axes[0]
    ax.plot(df8["year"], df8["total_density_unl"],
            marker="s", color="tab:blue", label="DE unlimited", linewidth=2)
    ax.plot(df8["year"], df8["total_density_lim"],
            marker="^", color="tab:red", label="DE speed-limited",
            linewidth=2, linestyle="--")
    ax.set_title("All accidents per 100 km", fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Accidents per 100 km")
    ax.legend()

    ax2 = axes[1]
    ax2.plot(df8["year"], df8["fatal_density_unl"],
             marker="s", color="tab:blue", label="DE unlimited", linewidth=2)
    ax2.plot(df8["year"], df8["fatal_density_lim"],
             marker="^", color="tab:red", label="DE speed-limited",
             linewidth=2, linestyle="--")
    ax2.set_title("Fatal accidents per 100 km", fontsize=12)
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Fatal accidents per 100 km")
    ax2.legend()

    fig.suptitle("German Autobahn Accident Density: Unlimited vs Speed-Limited",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save(fig, "fig08_accident_density_de")

    print("  DE accident density (accidents per 100 km / year):")
    print(
        df8[["year", "total_density_unl", "total_density_lim",
             "fatal_density_unl", "fatal_density_lim"]]
        .rename(columns={
            "total_density_unl": "total/100km_unl",
            "total_density_lim": "total/100km_lim",
            "fatal_density_unl": "fatal/100km_unl",
            "fatal_density_lim": "fatal/100km_lim",
        })
        .to_string(index=False, float_format=lambda x: f"{x:.3f}")
    )


def fig09() -> None:
    """Injury severity pyramid (fatal : serious : slight ratios, pooled 2016–2024)."""
    print("Fig 09: Injury severity pyramid")
    df_ua = _load_ua()
    df_nl = _load_nl()

    de_mw = df_ua[df_ua["on_motorway"] & df_ua["year"].between(2016, 2024)]

    def _pyramid_counts(sub: pd.DataFrame) -> dict:
        counts  = sub["severity"].value_counts()
        fatal   = int(counts.get("fatal",          0))
        serious = int(counts.get("serious_injury",  0))
        slight  = int(counts.get("slight_injury",   0))
        total   = fatal + serious + slight
        if total == 0:
            return dict(fatal=0, serious=0, slight=0,
                        pct_fatal=0.0, pct_serious=0.0, pct_slight=0.0, total=0)
        return dict(
            fatal=fatal, serious=serious, slight=slight,
            pct_fatal   = fatal   / total * 100,
            pct_serious = serious / total * 100,
            pct_slight  = slight  / total * 100,
            total=total,
        )

    de_unl_pyr = _pyramid_counts(de_mw[de_mw["on_unlimited"]])
    de_lim_pyr = _pyramid_counts(de_mw[de_mw["on_limited_mw"]])

    # NL: use only fatal + serious + slight as denominator (exclude material/property-damage-only)
    # This makes it comparable to DE injury-accident data which excludes property-damage-only.
    # Note: serious and slight are not separately recorded in rws_motorway_annual.parquet (=0),
    # so the NL pyramid reflects 100% fatal among recorded injury accidents.
    nl_sub        = df_nl[df_nl["year"].between(2016, 2024)]
    nl_fatal_n    = int(nl_sub["fatal"].sum())
    nl_serious_n  = int(nl_sub["serious"].sum())
    nl_slight_n   = int(nl_sub["slight"].sum())
    nl_total_n    = nl_fatal_n + nl_serious_n + nl_slight_n
    if nl_total_n > 0:
        nl_pyr = dict(
            fatal=nl_fatal_n,
            serious=nl_serious_n,
            slight=nl_slight_n,
            total=nl_total_n,
            pct_fatal   = nl_fatal_n   / nl_total_n * 100,
            pct_serious = nl_serious_n / nl_total_n * 100,
            pct_slight  = nl_slight_n  / nl_total_n * 100,
        )
    else:
        nl_pyr = None

    # Print summary — verify each group sums to 100%
    print(f"\n  {'Group':<28} {'Fatal':>8} {'Serious':>8} {'Slight':>8} {'Total':>8}"
          f"  {'%Fatal':>7} {'%Serious':>8} {'%Slight':>8}  {'Sum%':>6}")
    print("  " + "-" * 100)
    for lbl, d in [("DE unlimited Autobahn", de_unl_pyr),
                   ("DE speed-limited Autobahn", de_lim_pyr)]:
        row_sum = d["pct_fatal"] + d["pct_serious"] + d["pct_slight"]
        print(f"  {lbl:<28} {d['fatal']:>8,} {d['serious']:>8,} {d['slight']:>8,} "
              f"{d['total']:>8,}  {d['pct_fatal']:>6.2f}% {d['pct_serious']:>7.2f}% "
              f"{d['pct_slight']:>7.2f}%  {row_sum:>5.1f}%")
    if nl_pyr:
        row_sum = nl_pyr["pct_fatal"] + nl_pyr["pct_serious"] + nl_pyr["pct_slight"]
        print(f"  {'NL (injury accidents only)':<28} {nl_pyr['fatal']:>8,} "
              f"{nl_pyr['serious']:>8,} {nl_pyr['slight']:>8,} {nl_pyr['total']:>8,}  "
              f"{nl_pyr['pct_fatal']:>6.2f}% {nl_pyr['pct_serious']:>7.2f}% "
              f"{nl_pyr['pct_slight']:>7.2f}%  {row_sum:>5.1f}%")
        print("  Note: NL BRON data does not separately record serious/slight injury accidents")
        print("        on motorways; serious=0, slight=0 → pyramid shows 100% fatal.")
    print()

    # Plot — unified layout showing all 3 groups with 3-bar pyramid
    groups   = ["DE unlimited", "DE speed-limited", "NL motorway"]
    pyrs     = [de_unl_pyr, de_lim_pyr, nl_pyr if nl_pyr else dict(
        pct_fatal=0.0, pct_serious=0.0, pct_slight=0.0)]
    pct_fatal = [p["pct_fatal"]   for p in pyrs]
    pct_ser   = [p["pct_serious"] for p in pyrs]
    pct_sli   = [p["pct_slight"]  for p in pyrs]
    y_pos, bar_h = np.arange(len(groups)), 0.55

    fig, ax = plt.subplots(figsize=(12, 5))
    bars_f  = ax.barh(y_pos, pct_fatal, bar_h, label="Fatal",         color="#d62728")
    bars_s  = ax.barh(y_pos, pct_ser,   bar_h, left=pct_fatal,        label="Serious", color="#ff7f0e")
    bars_sl = ax.barh(y_pos, pct_sli,   bar_h,
                      left=[a + b for a, b in zip(pct_fatal, pct_ser)],
                      label="Slight", color="#aec7e8")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(groups, fontsize=12)
    ax.set_xlabel("Share of injury accidents (%)", fontsize=11)
    ax.set_xlim(0, 100)
    ax.set_title(
        "Injury Severity Pyramid (2016–2024 pooled)\n"
        "Denominator: injury accidents only (fatal + serious + slight; excludes property-damage-only)",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="lower right", fontsize=10)

    # Add percentage labels
    for i, (f, s, sl) in enumerate(zip(pct_fatal, pct_ser, pct_sli)):
        if f > 0.5:
            ax.text(f / 2, i, f"{f:.1f}%", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
        if s > 1:
            ax.text(f + s / 2, i, f"{s:.1f}%", ha="center", va="center",
                    fontsize=9, color="white")
        if sl > 1:
            ax.text(f + s + sl / 2, i, f"{sl:.1f}%", ha="center", va="center",
                    fontsize=9, color="black")

    # Annotation for NL data limitation
    if nl_pyr and nl_pyr["pct_slight"] == 0.0:
        ax.annotate(
            "NL: serious/slight\nnot recorded separately",
            xy=(50, 2), ha="center", va="center",
            fontsize=8, color="#555555", style="italic",
        )

    sns.despine()
    plt.tight_layout()
    _save(fig, "fig09_injury_pyramid")


# ── Hypothesis testing figures ────────────────────────────────────────────────

def fig10() -> None:
    """H3: Diverging safety trends — Poisson regression on annual fatality rates.

    Johansson (1996) method: fatal_count ~ year with log(total) offset.
    Tests whether limited Autobahn shows a significant downward trend while
    unlimited does not (or improves more slowly).
    """
    print("Fig 10: H3 — Diverging safety trends (Johansson 1996 Poisson regression)")
    df_ua = _load_ua()

    # Build annual data per group
    def _annual(df: pd.DataFrame, km: float) -> pd.DataFrame:
        by_year = (
            df.groupby("year")
            .agg(
                total=("severity", "count"),
                fatal=("severity", lambda x: (x == "fatal").sum()),
            )
            .reset_index()
        )
        by_year["fatal_rate"] = by_year["fatal"] / by_year["total"]
        by_year["log_offset"] = np.log(by_year["total"])
        by_year["year_c"] = by_year["year"] - by_year["year"].mean()  # centre for numerics
        return by_year

    df_unl = _annual(df_ua[df_ua["on_unlimited"]], KM_DE_UNLIMITED)
    df_lim = _annual(df_ua[df_ua["on_limited_mw"]], KM_DE_LIMITED)

    # Fit separate Poisson models
    results: dict[str, dict] = {}
    for label, df_grp in [("Unlimited", df_unl), ("Limited", df_lim)]:
        model = smf.glm(
            "fatal ~ year_c",
            data=df_grp,
            family=__import__("statsmodels.genmod.families", fromlist=["Poisson"]).Poisson(),
            offset=df_grp["log_offset"],
        ).fit(disp=False)
        beta = model.params["year_c"]
        pval = model.pvalues["year_c"]
        pct_per_yr = (np.exp(beta) - 1) * 100
        results[label] = {
            "model":      model,
            "beta":       beta,
            "pval":       pval,
            "pct_per_yr": pct_per_yr,
            "df_grp":     df_grp,
        }
        print(f"  {label}: β_year = {beta:.4f}, p = {pval:.4f}, "
              f"%change/yr = {pct_per_yr:+.2f}%")

    # Combined model: fatal ~ year + group + year:group
    df_unl_c = df_unl.copy(); df_unl_c["group"] = 0  # 0 = limited (reference)
    df_lim_c = df_lim.copy(); df_lim_c["group"] = 0
    df_unl_c["group"] = 1   # 1 = unlimited
    df_combined_m = pd.concat([df_unl_c, df_lim_c], ignore_index=True)
    model_comb = smf.glm(
        "fatal ~ year_c + group + year_c:group",
        data=df_combined_m,
        family=__import__("statsmodels.genmod.families", fromlist=["Poisson"]).Poisson(),
        offset=df_combined_m["log_offset"],
    ).fit(disp=False)
    interaction_beta = model_comb.params["year_c:group"]
    interaction_p    = model_comb.pvalues["year_c:group"]
    print(f"\n  Combined model interaction (year × group):")
    print(f"  β_interaction = {interaction_beta:.4f}, p = {interaction_p:.4f}")
    print(f"  {'Significant' if interaction_p < 0.05 else 'Not significant'} "
          f"divergence in trends (α=0.05)")

    # Fitted values for plotting
    def _fitted_rate(res: dict) -> pd.Series:
        df_g = res["df_grp"].copy()
        pred_log_mu = res["model"].predict(df_g)
        return pred_log_mu / df_g["total"]

    # Plot
    fig, ax = plt.subplots(figsize=(11, 6))

    colors = {"Unlimited": "#e63946", "Limited": "#457b9d"}
    markers = {"Unlimited": "o", "Limited": "s"}

    for label, res in results.items():
        df_g = res["df_grp"]
        ax.scatter(df_g["year"], df_g["fatal_rate"] * 1000,
                   color=colors[label], marker=markers[label],
                   s=55, zorder=5, label=f"{label} (observed)")
        fitted = _fitted_rate(res)
        ax.plot(df_g["year"], fitted * 1000,
                color=colors[label], linewidth=2, linestyle="--",
                label=f"{label} fitted: {res['pct_per_yr']:+.1f}%/yr "
                      f"(p={res['pval']:.3f})")

    ax.set_title(
        "H3: Annual fatality rate with Poisson trend (Johansson 1996)\n"
        f"Unlimited: {results['Unlimited']['pct_per_yr']:+.1f}%/yr (p={results['Unlimited']['pval']:.3f}) | "
        f"Limited: {results['Limited']['pct_per_yr']:+.1f}%/yr (p={results['Limited']['pval']:.3f})\n"
        f"Interaction β={interaction_beta:.4f} (p={interaction_p:.3f})",
        fontsize=11, fontweight="bold",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Fatalities per 1000 accidents")
    ax.legend(fontsize=9)
    sns.despine()
    plt.tight_layout()
    _save(fig, "fig10_trend_analysis")


def fig11() -> None:
    """H4: Power Model back-calculation — observed vs predicted severity ratios.

    Uses BASt 2019 speed data and Elvik (2013) motorway exponents to predict
    accident ratios from the speed difference, then compares to observed.
    """
    print("Fig 11: H4 — Power Model back-calculation (Elvik 2013)")
    df_ua = _load_ua()

    # ── Speed constants (BASt 2019: Verkehr auf Bundesautobahnen annual report) ──
    V_UNLIMITED = 135.0   # mean speed on unlimited sections (km/h), BASt 2019
    V_LIMITED   = 118.0   # mean speed on limited sections   (km/h), BASt 2019
    SPEED_RATIO = V_UNLIMITED / V_LIMITED

    # ── Elvik (2013) motorway exponents with 95% CI ──
    EXPONENTS = {
        "Fatal accidents":          {"exp": 4.1, "lo": 2.9, "hi": 5.3},
        "Serious injury accidents":  {"exp": 2.6, "lo": 2.6, "hi": 2.6},  # point estimate only
        "All injury accidents":      {"exp": 1.6, "lo": 1.6, "hi": 1.6},
    }

    # ── Observed ratios from Unfallatlas (unlimited / limited, per km) ──
    mw_unl = df_ua[df_ua["on_unlimited"]]
    mw_lim = df_ua[df_ua["on_limited_mw"]]

    n_fatal_unl    = (mw_unl["severity"] == "fatal").sum()
    n_fatal_lim    = (mw_lim["severity"] == "fatal").sum()
    n_serious_unl  = (mw_unl["severity"] == "serious_injury").sum()
    n_serious_lim  = (mw_lim["severity"] == "serious_injury").sum()
    n_total_unl    = len(mw_unl)
    n_total_lim    = len(mw_lim)

    # Per-km rates then ratio
    rate_fatal_unl   = n_fatal_unl   / KM_DE_UNLIMITED
    rate_fatal_lim   = n_fatal_lim   / KM_DE_LIMITED
    rate_serious_unl = n_serious_unl / KM_DE_UNLIMITED
    rate_serious_lim = n_serious_lim / KM_DE_LIMITED
    rate_total_unl   = n_total_unl   / KM_DE_UNLIMITED
    rate_total_lim   = n_total_lim   / KM_DE_LIMITED

    obs_fatal   = rate_fatal_unl   / rate_fatal_lim
    obs_serious = rate_serious_unl / rate_serious_lim
    obs_total   = rate_total_unl   / rate_total_lim

    OBSERVED = {
        "Fatal accidents":           obs_fatal,
        "Serious injury accidents":  obs_serious,
        "All injury accidents":      obs_total,
    }

    # ── Predicted ratios ──
    rows = []
    for label, ex in EXPONENTS.items():
        pred_mid = SPEED_RATIO ** ex["exp"]
        pred_lo  = SPEED_RATIO ** ex["lo"]
        pred_hi  = SPEED_RATIO ** ex["hi"]
        obs_val  = OBSERVED[label]
        rows.append({
            "severity":   label,
            "predicted":  pred_mid,
            "pred_lo":    pred_lo,
            "pred_hi":    pred_hi,
            "observed":   obs_val,
        })
        print(f"  {label}:")
        print(f"    Predicted: {pred_mid:.3f} (95% CI {pred_lo:.3f}–{pred_hi:.3f})")
        print(f"    Observed:  {obs_val:.3f}")
        interp = "≈ predicted (speed explains gap)" if abs(obs_val - pred_mid) / pred_mid < 0.25 \
            else ("< predicted (confounding advantages)" if obs_val < pred_mid
                  else "> predicted (additional speed-independent risks)")
        print(f"    Interpretation: {interp}")

    df_res = pd.DataFrame(rows)

    # ── Plot ──
    fig, ax = plt.subplots(figsize=(10, 6))
    x       = np.arange(len(df_res))
    width   = 0.32
    colors  = {"predicted": "#457b9d", "observed": "#e63946"}

    bars_pred = ax.bar(x - width / 2, df_res["predicted"], width,
                       color=colors["predicted"], label="Power Model prediction", alpha=0.85)
    bars_obs  = ax.bar(x + width / 2, df_res["observed"],  width,
                       color=colors["observed"],  label="Observed (per km)", alpha=0.85)

    # Error bars (CI) on predicted
    err_lo = df_res["predicted"] - df_res["pred_lo"]
    err_hi = df_res["pred_hi"]   - df_res["predicted"]
    ax.errorbar(
        x - width / 2, df_res["predicted"],
        yerr=[err_lo.values, err_hi.values],
        fmt="none", color="black", capsize=5, linewidth=1.5,
        label="95% CI (Elvik 2013 exponent)",
    )

    ax.bar_label(bars_pred, fmt="%.2f", padding=4, fontsize=9, fontweight="bold")
    ax.bar_label(bars_obs,  fmt="%.2f", padding=4, fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(df_res["severity"], fontsize=11)
    ax.set_ylabel("Accident rate ratio (unlimited / limited, per km)", fontsize=11)
    ax.axhline(1.0, color="grey", linestyle=":", linewidth=1)
    ax.set_title(
        f"H4: Power Model vs Observed Accident Rate Ratios\n"
        f"Speed: {V_UNLIMITED} km/h (unlimited) vs {V_LIMITED} km/h (limited) "
        f"— BASt 2019 | Elvik (2013) exponents",
        fontsize=11, fontweight="bold",
    )
    ax.legend(fontsize=9)
    sns.despine()
    plt.tight_layout()
    _save(fig, "fig11_power_model_check")


def fig12() -> None:
    """H5: Crash type distribution — Safe System threshold analysis (Doecke 2018).

    Tests whether unlimited sections have a higher proportion of high-energy
    crash types (head-on: UTYP1=3, run-off: UTYP1=7).
    Also computes case fatality rate by crash type × speed regime.
    """
    print("Fig 12: H5 — Crash type distribution / Safe System threshold (Doecke 2018)")
    df_ua = _load_ua()

    # Filter to motorway accidents only
    mw = df_ua[df_ua["on_motorway"]].copy()

    # ── UTYP1 groupings ──
    # High-energy (unsafe at high speed per Doecke 2018)
    #   3 = head-on collision, 7 = run-off road
    # Medium-energy:
    #   2 = rear-end/sideswipe same direction, 6 = stationary traffic collision
    # Other: 1=parked vehicle, 4=junction, 5=entering vehicle
    def _energy_group(utyp1: int) -> str:
        if utyp1 in (3, 7):
            return "High-energy\n(head-on, run-off)"
        if utyp1 in (2, 6):
            return "Medium-energy\n(rear-end, stationary)"
        return "Other"

    mw["energy_group"] = mw["UTYP1"].map(_energy_group)
    mw["is_fatal"]     = (mw["severity"] == "fatal").astype(int)

    # ── Stacked bar: proportion of each collision type ──
    mw_unl = mw[mw["on_unlimited"]].copy()
    mw_lim = mw[mw["on_limited_mw"]].copy()

    utyp_labels = {
        1: "Parked vehicle (1)",
        2: "Rear-end / sideswipe (2)",
        3: "Head-on (3)",
        4: "Junction (4)",
        5: "Entering vehicle (5)",
        6: "Stationary traffic (6)",
        7: "Run-off road (7)",
    }

    def _utyp_pct(sub: pd.DataFrame) -> pd.Series:
        counts = sub["UTYP1"].value_counts()
        pct = (counts / counts.sum() * 100).reindex(range(1, 8), fill_value=0.0)
        return pct

    pct_unl = _utyp_pct(mw_unl)
    pct_lim = _utyp_pct(mw_lim)

    # Chi-squared test for independence
    contingency = pd.DataFrame({"unlimited": mw_unl["UTYP1"].value_counts(),
                                 "limited":   mw_lim["UTYP1"].value_counts()}).fillna(0)
    chi2, chi2_p, chi2_dof, _ = stats.chi2_contingency(contingency.values)
    print(f"\n  Chi-squared test (UTYP1 distribution, unlimited vs limited):")
    print(f"  χ²={chi2:.2f}, df={chi2_dof}, p={chi2_p:.2e}")

    # High-energy proportions
    he_unl = pct_unl[[3, 7]].sum()
    he_lim = pct_lim[[3, 7]].sum()
    print(f"\n  High-energy crash type proportions:")
    print(f"    Unlimited: {he_unl:.1f}%  |  Limited: {he_lim:.1f}%  |  "
          f"Δ = {he_unl - he_lim:+.1f}pp")

    # ── Case fatality rates by crash type × speed regime ──
    cfr_rows = []
    for utyp, ulabel in utyp_labels.items():
        for grp_label, sub in [("Unlimited", mw_unl), ("Limited", mw_lim)]:
            s = sub[sub["UTYP1"] == utyp]
            if len(s) > 0:
                cfr = s["is_fatal"].mean() * 100
                cfr_rows.append({
                    "UTYP1": utyp, "label": ulabel,
                    "group": grp_label,
                    "cfr":   cfr,
                    "n":     len(s),
                })
    df_cfr = pd.DataFrame(cfr_rows)

    print("\n  Case fatality rate (%) by crash type:")
    for utyp in range(1, 8):
        row_unl = df_cfr[(df_cfr["UTYP1"] == utyp) & (df_cfr["group"] == "Unlimited")]
        row_lim = df_cfr[(df_cfr["UTYP1"] == utyp) & (df_cfr["group"] == "Limited")]
        cfr_unl = row_unl["cfr"].values[0] if len(row_unl) else 0.0
        cfr_lim = row_lim["cfr"].values[0] if len(row_lim) else 0.0
        n_unl   = row_unl["n"].values[0]   if len(row_unl) else 0
        n_lim   = row_lim["n"].values[0]   if len(row_lim) else 0
        print(f"    UTYP1={utyp} {utyp_labels[utyp]:<30}: "
              f"Unlimited {cfr_unl:.2f}% (n={n_unl:,})  "
              f"Limited {cfr_lim:.2f}% (n={n_lim:,})")

    # ── Figure: 2 panels ──
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Panel 1: stacked bar of UTYP1 proportions
    ax1 = axes[0]
    x_pos = np.array([0, 1])
    bottom_arr = np.zeros(2)

    # Colour scheme: highlight high-energy types
    type_colors = {
        1: "#adb5bd",  # grey     — parked vehicle
        2: "#74b9ff",  # light blue — rear-end
        3: "#d62728",  # red       — head-on (HIGH ENERGY)
        4: "#adb5bd",
        5: "#adb5bd",
        6: "#636e72",  # dark grey — stationary
        7: "#ff7675",  # salmon    — run-off (HIGH ENERGY)
    }

    for utyp in [1, 2, 3, 4, 5, 6, 7]:
        heights = np.array([pct_unl[utyp], pct_lim[utyp]])
        bars = ax1.bar(
            x_pos, heights, 0.5,
            bottom=bottom_arr,
            color=type_colors[utyp],
            label=utyp_labels[utyp],
            edgecolor="white", linewidth=0.4,
        )
        for i, (h, b) in enumerate(zip(heights, bottom_arr)):
            if h > 3:
                ax1.text(x_pos[i], b + h / 2, f"{h:.1f}%",
                         ha="center", va="center", fontsize=8,
                         color="white" if utyp in (3, 7) else "black",
                         fontweight="bold" if utyp in (3, 7) else "normal")
        bottom_arr += heights

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(["Unlimited\nAutobahn", "Speed-limited\nAutobahn"], fontsize=11)
    ax1.set_ylabel("Share of motorway accidents (%)", fontsize=10)
    ax1.set_title(
        f"H5: Crash type distribution\n"
        f"High-energy (red/salmon): Unlimited {he_unl:.1f}%, Limited {he_lim:.1f}%\n"
        f"χ²={chi2:.1f}, p={chi2_p:.2e}",
        fontsize=10, fontweight="bold",
    )
    ax1.set_ylim(0, 105)
    ax1.legend(loc="upper right", fontsize=7, ncol=1, framealpha=0.8)
    ax1.annotate(
        'Doecke (2018): Safe System threshold\nhead-on: 50 km/h | run-off: 70 km/h',
        xy=(0.5, 0.03), xycoords='axes fraction',
        ha='center', fontsize=8, style='italic', color='#555555',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f8f9fa', alpha=0.7),
    )

    # Panel 2: case fatality rate by crash type × group
    ax2 = axes[1]
    utyp_order = list(range(1, 8))
    x2         = np.arange(len(utyp_order))
    w2         = 0.35

    cfr_unl_vals = []
    cfr_lim_vals = []
    for utyp in utyp_order:
        row_u = df_cfr[(df_cfr["UTYP1"] == utyp) & (df_cfr["group"] == "Unlimited")]
        row_l = df_cfr[(df_cfr["UTYP1"] == utyp) & (df_cfr["group"] == "Limited")]
        cfr_unl_vals.append(row_u["cfr"].values[0] if len(row_u) else 0.0)
        cfr_lim_vals.append(row_l["cfr"].values[0] if len(row_l) else 0.0)

    b_unl = ax2.bar(x2 - w2 / 2, cfr_unl_vals, w2, color="#e63946",
                    label="Unlimited", alpha=0.85)
    b_lim = ax2.bar(x2 + w2 / 2, cfr_lim_vals, w2, color="#457b9d",
                    label="Speed-limited", alpha=0.85)

    ax2.set_xticks(x2)
    ax2.set_xticklabels(
        [utyp_labels[u].split(" (")[0].replace("/", "/\n") for u in utyp_order],
        fontsize=8,
    )
    ax2.set_ylabel("Case fatality rate (%)", fontsize=10)
    ax2.set_title(
        "Case fatality rate by collision type\n"
        "(fatal / total accidents of that type)",
        fontsize=10, fontweight="bold",
    )
    ax2.legend(fontsize=9)

    # Highlight high-energy columns
    for idx, utyp in enumerate(utyp_order):
        if utyp in (3, 7):
            ax2.axvspan(idx - 0.5, idx + 0.5, alpha=0.08, color="red", zorder=0)

    ax2.annotate(
        "Highlighted: high-energy types\n(head-on=3, run-off=7)",
        xy=(0.98, 0.97), xycoords='axes fraction',
        ha='right', va='top', fontsize=8, color='darkred',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff0f0', alpha=0.8),
    )

    sns.despine()
    fig.suptitle(
        "H5: Safe System crash type analysis (Doecke 2018)\n"
        "Unlimited vs speed-limited Autobahn sections",
        fontsize=12, fontweight="bold",
    )
    plt.tight_layout()
    _save(fig, "fig12_crash_type_analysis")


# ── Registry ───────────────────────────────────────────────────────────────────
FIGURE_REGISTRY: dict[int, Callable[[], None]] = {
    1:  fig01,
    2:  fig02,
    3:  fig03,
    4:  fig04,
    5:  fig05,
    6:  fig06,
    7:  fig07,
    8:  fig08,
    9:  fig09,
    10: fig10,
    11: fig11,
    12: fig12,
}


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate analysis figures for the Autobahn speed-safety study.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Generate all figures:\n"
            "    .venv/bin/python scripts/create_figures.py\n\n"
            "  Generate only figures 7, 8, 9:\n"
            "    .venv/bin/python scripts/create_figures.py --figures 7 8 9"
        ),
    )
    parser.add_argument(
        "--figures",
        nargs="+",
        type=int,
        choices=sorted(FIGURE_REGISTRY),
        metavar="N",
        help=(
            f"Figures to generate (1–{max(FIGURE_REGISTRY)}). "
            "Defaults to all figures when omitted."
        ),
    )
    args = parser.parse_args()

    sns.set_theme(style="whitegrid")
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    to_run = sorted(args.figures or FIGURE_REGISTRY.keys())

    print(f"\n{'='*60}")
    print(f"Generating figures: {to_run}")
    print(f"Output directory  : {FIG_DIR.resolve()}")
    print(f"{'='*60}\n")

    errors: list[tuple[int, Exception]] = []
    for n in to_run:
        try:
            FIGURE_REGISTRY[n]()
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR in fig{n:02d}: {exc}")
            errors.append((n, exc))

    print(f"\n{'='*60}")
    if errors:
        print(f"Completed with {len(errors)} error(s):")
        for n, exc in errors:
            print(f"  fig{n:02d}: {exc}")
        sys.exit(1)
    else:
        generated = [n for n in to_run if n not in {e[0] for e in errors}]
        print(f"All {len(generated)} figure(s) generated successfully.")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
