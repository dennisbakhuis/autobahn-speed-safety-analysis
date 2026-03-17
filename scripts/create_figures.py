"""Generate all analysis figures (fig01–fig09) for the Autobahn speed-safety analysis.

Loads processed data from data/processed/ and saves figures to output/figures/.
Mirrors the logic in notebooks 03–05 and consolidates scripts/03_create_plots.py.

Usage (from project root):
    .venv/bin/python scripts/create_figures.py              # all figures
    .venv/bin/python scripts/create_figures.py --figures 7 8 9   # subset
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
    """Fatal accident density per 100 km of network (DE + NL)."""
    print("Fig 07: Fatal accidents per 100 km of road per year")
    df_ua = _load_ua()
    df_nl = _load_nl()

    # Germany
    de_mw  = df_ua[df_ua["on_motorway"]]
    de_unl_fatal = (
        de_mw[de_mw["on_unlimited"] & (de_mw["severity"] == "fatal")]
        .groupby("year").size().rename("fatal_unl")
    )
    de_lim_fatal = (
        de_mw[de_mw["on_limited_mw"] & (de_mw["severity"] == "fatal")]
        .groupby("year").size().rename("fatal_lim")
    )
    de_fatal = pd.concat([de_unl_fatal, de_lim_fatal], axis=1).reset_index()
    de_fatal["density_unl"] = de_fatal["fatal_unl"] / KM_DE_UNLIMITED * 100
    de_fatal["density_lim"] = de_fatal["fatal_lim"] / KM_DE_LIMITED   * 100

    # Netherlands
    nl_fatal = df_nl[["year", "fatal"]].copy()
    nl_fatal["density_nl"] = nl_fatal["fatal"] / KM_NL * 100

    common_years = sorted(set(de_fatal["year"]) & set(nl_fatal["year"]))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

    # Left: full range overlay
    ax = axes[0]
    ax.plot(nl_fatal["year"], nl_fatal["density_nl"],
            marker="o", color="tab:orange", label="NL motorways", linewidth=2)
    ax.plot(de_fatal["year"], de_fatal["density_unl"],
            marker="s", color="tab:blue", label="DE unlimited", linewidth=2)
    ax.plot(de_fatal["year"], de_fatal["density_lim"],
            marker="^", color="tab:red", label="DE speed-limited",
            linewidth=2, linestyle="--")
    ax.set_title("Fatal accident density (full range)", fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Fatal accidents per 100 km")
    ax.legend()

    # Right: common years only
    ax2 = axes[1]
    nl_c = nl_fatal[nl_fatal["year"].isin(common_years)]
    de_c = de_fatal[de_fatal["year"].isin(common_years)]
    ax2.plot(nl_c["year"], nl_c["density_nl"],
             marker="o", color="tab:orange", label="NL motorways", linewidth=2)
    ax2.plot(de_c["year"], de_c["density_unl"],
             marker="s", color="tab:blue", label="DE unlimited", linewidth=2)
    ax2.plot(de_c["year"], de_c["density_lim"],
             marker="^", color="tab:red", label="DE speed-limited",
             linewidth=2, linestyle="--")
    ax2.set_title(
        f"Fatal accident density (common years: {common_years[0]}–{common_years[-1]})",
        fontsize=12,
    )
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Fatal accidents per 100 km")
    ax2.legend()

    fig.suptitle("Fatal Accidents per 100 km of Motorway Network",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save(fig, "fig07_fatal_accidents_per_100km")

    # Summary table
    summary = de_fatal[["year", "density_unl", "density_lim"]].rename(
        columns={"density_unl": "DE_unlimited", "density_lim": "DE_limited"})
    summary = summary.merge(
        nl_fatal[["year", "density_nl"]].rename(columns={"density_nl": "NL"}),
        on="year", how="outer",
    ).sort_values("year")
    print("  Fatal accident density (per 100 km / year):")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


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

    # NL: only fatal + material available
    nl_sub       = df_nl[df_nl["year"].between(2016, 2024)]
    nl_fatal_n   = int(nl_sub["fatal"].sum())
    nl_material_n = int(nl_sub["material"].sum())
    nl_total_n   = nl_fatal_n + nl_material_n
    nl_pyr = (
        dict(
            fatal=nl_fatal_n,
            material=nl_material_n,
            pct_fatal    = nl_fatal_n    / nl_total_n * 100,
            pct_material = nl_material_n / nl_total_n * 100,
        )
        if nl_total_n > 0 else None
    )

    # Print summary
    print(f"\n  {'Group':<28} {'Fatal':>8} {'Serious':>8} {'Slight':>8} {'Total':>8}"
          f"  {'%Fatal':>7} {'%Serious':>8} {'%Slight':>8}")
    print("  " + "-" * 88)
    for lbl, d in [("DE unlimited Autobahn", de_unl_pyr),
                   ("DE speed-limited Autobahn", de_lim_pyr)]:
        print(f"  {lbl:<28} {d['fatal']:>8,} {d['serious']:>8,} {d['slight']:>8,} "
              f"{d['total']:>8,}  {d['pct_fatal']:>6.2f}% {d['pct_serious']:>7.2f}% "
              f"{d['pct_slight']:>7.2f}%")
    if nl_pyr:
        print(f"  {'NL (fatal vs prop-damage)':<28} {nl_pyr['fatal']:>8,} {'N/A':>8} "
              f"{'N/A':>8} {nl_total_n:>8,}  {nl_pyr['pct_fatal']:>6.2f}%"
              f" {'N/A':>7} {'N/A':>7}")
    print()

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Panel 1: DE injury pyramid
    groups_de = ["DE unlimited", "DE speed-limited"]
    pct_fatal = [de_unl_pyr["pct_fatal"],  de_lim_pyr["pct_fatal"]]
    pct_ser   = [de_unl_pyr["pct_serious"], de_lim_pyr["pct_serious"]]
    pct_sli   = [de_unl_pyr["pct_slight"],  de_lim_pyr["pct_slight"]]
    y_pos, bar_h = np.arange(len(groups_de)), 0.5

    ax = axes[0]
    ax.barh(y_pos, pct_fatal, bar_h, label="Fatal",   color="#d62728")
    ax.barh(y_pos, pct_ser,   bar_h, left=pct_fatal,  label="Serious", color="#ff7f0e")
    ax.barh(y_pos, pct_sli,   bar_h,
            left=[a + b for a, b in zip(pct_fatal, pct_ser)],
            label="Slight", color="#aec7e8")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(groups_de)
    ax.set_xlabel("Share of injury accidents (%)")
    ax.set_xlim(0, 100)
    ax.set_title("DE: injury severity pyramid\n(fatal / serious / slight)", fontsize=11)
    ax.legend(loc="lower right")

    # Add percentage labels
    for i, (f, s, sl) in enumerate(zip(pct_fatal, pct_ser, pct_sli)):
        if f > 1:
            ax.text(f / 2, i, f"{f:.1f}%", ha="center", va="center",
                    fontsize=9, color="white", fontweight="bold")
        if s > 2:
            ax.text(f + s / 2, i, f"{s:.1f}%", ha="center", va="center",
                    fontsize=9, color="white")
        if sl > 2:
            ax.text(f + s + sl / 2, i, f"{sl:.1f}%", ha="center", va="center",
                    fontsize=9, color="black")

    # Panel 2: NL fatal vs property-damage
    ax2 = axes[1]
    if nl_pyr:
        ax2.barh([0], [nl_pyr["pct_fatal"]],    bar_h,
                 label="Fatal",                  color="#d62728")
        ax2.barh([0], [nl_pyr["pct_material"]], bar_h,
                 left=[nl_pyr["pct_fatal"]],
                 label="Property damage only",   color="#c7c7c7")
        ax2.set_yticks([0])
        ax2.set_yticklabels(["NL motorways"])
        ax2.set_xlabel("Share of accidents (%)")
        ax2.set_xlim(0, 100)
        ax2.set_title("NL: fatal vs property-damage-only\n(serious/slight not in dataset)",
                      fontsize=11)
        ax2.legend(loc="lower right")
        ax2.text(nl_pyr["pct_fatal"] / 2, 0,
                 f"{nl_pyr['pct_fatal']:.2f}%",
                 ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        ax2.text(nl_pyr["pct_fatal"] + nl_pyr["pct_material"] / 2, 0,
                 f"{nl_pyr['pct_material']:.1f}%",
                 ha="center", va="center", fontsize=9, color="black")
    else:
        ax2.text(0.5, 0.5, "NL data not available",
                 transform=ax2.transAxes, ha="center", va="center")

    fig.suptitle("Injury Severity Pyramid (2016–2024 pooled)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save(fig, "fig09_injury_pyramid")


# ── Registry ───────────────────────────────────────────────────────────────────
FIGURE_REGISTRY: dict[int, Callable[[], None]] = {
    1: fig01,
    2: fig02,
    3: fig03,
    4: fig04,
    5: fig05,
    6: fig06,
    7: fig07,
    8: fig08,
    9: fig09,
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
