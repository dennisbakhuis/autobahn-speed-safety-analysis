"""Create all analysis plots for the Autobahn speed-safety analysis.

Requires processed data from 02_process_data.py.
Saves all figures to output/figures/.

Run from project root:
    uv run python scripts/03_create_plots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autobahn_safety.data_loaders import load_destatis_autobahn

DATA_RAW = Path("data/raw")
DATA_PROC = Path("data/processed")
FIG_DIR = Path("output/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
PALETTE = {
    "DE: Unlimited Autobahn": "#e63946",
    "DE: Limited Autobahn": "#457b9d",
    "NL: Motorway": "#2a9d8f",
}


def save(fig: plt.Figure, name: str) -> None:
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.close(fig)


# ── Load data ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Loading processed data")
print("=" * 60)

ua_path = DATA_PROC / "unfallatlas_classified.parquet"
nl_path = DATA_PROC / "rws_motorway_annual.parquet"
destatis_path = DATA_RAW / "germany" / "destatis" / "destatis_verkehrsunfaelle_zeitreihen.xlsx"

if not ua_path.exists():
    sys.exit("ERROR: unfallatlas_classified.parquet not found. Run 02_process_data.py first.")
if not nl_path.exists():
    sys.exit("ERROR: rws_motorway_annual.parquet not found. Run 02_process_data.py first.")

df_ua = pd.read_parquet(ua_path)
df_nl_annual = pd.read_parquet(nl_path)
df_destatis = load_destatis_autobahn(destatis_path)

print(f"  Germany  : {len(df_ua):,} accident records")
print(f"  NL annual: {len(df_nl_annual)} years")
print(f"  Destatis : {len(df_destatis)} years")

# ── Build annual Germany summary ──────────────────────────────────────────────
groups_de = {
    "DE: Unlimited Autobahn": df_ua[df_ua["on_unlimited"]],
    "DE: Limited Autobahn": df_ua[df_ua["on_limited_mw"]],
}

de_annual = []
for label, grp in groups_de.items():
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
    de_annual.append(by_year)

df_de_annual = pd.concat(de_annual, ignore_index=True)

df_nl_plot = df_nl_annual[["year", "total", "fatal", "severity_idx"]].copy()
df_nl_plot["group"] = "NL: Motorway"
df_combined = pd.concat([df_de_annual, df_nl_plot], ignore_index=True)

# ── Fig 1: Long-term DE Autobahn trend (Destatis) ────────────────────────────
print("\nFig 1: Long-term Autobahn trend")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].plot(df_destatis["year"], df_destatis["accidents_personal_injury"],
             color="steelblue", linewidth=2)
axes[0].fill_between(df_destatis["year"], df_destatis["accidents_personal_injury"],
                     alpha=0.15, color="steelblue")
axes[0].set_title("Personal-injury accidents")
axes[0].set_xlabel("Year"); axes[0].set_ylabel("Accidents")

axes[1].plot(df_destatis["year"], df_destatis["accidents_fatal"],
             color="crimson", linewidth=2)
axes[1].fill_between(df_destatis["year"], df_destatis["accidents_fatal"],
                     alpha=0.15, color="crimson")
axes[1].set_title("Fatal accidents")
axes[1].set_xlabel("Year"); axes[1].set_ylabel("Fatal accidents")

fig.suptitle("German Autobahn: long-term safety trend (Destatis 1979–2021)",
             fontweight="bold", fontsize=13)
plt.tight_layout()
save(fig, "fig01_destatis_longterm")

# ── Fig 2: Severity index by road type (DE) ───────────────────────────────────
print("Fig 2: DE severity index by road type")
fig, ax = plt.subplots(figsize=(11, 5))

all_groups = {
    "Unlimited Autobahn": df_ua[df_ua["on_unlimited"]],
    "Speed-limited Autobahn": df_ua[df_ua["on_limited_mw"]],
    "Non-motorway": df_ua[~df_ua["on_motorway"]],
}
colors_de = {"Unlimited Autobahn": "#e63946", "Speed-limited Autobahn": "#457b9d",
             "Non-motorway": "#adb5bd"}

for label, grp in all_groups.items():
    by_year = (
        grp.groupby("year")
        .agg(total=("severity", "count"), fatal=("severity", lambda x: (x == "fatal").sum()))
        .reset_index()
    )
    by_year["severity_idx"] = by_year["fatal"] / by_year["total"]
    ax.plot(by_year["year"], by_year["severity_idx"] * 1000,
            marker="o", label=label, linewidth=2, color=colors_de[label])

ax.set_title("Germany: severity index by road type (fatalities per 1000 accidents)",
             fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Fatalities per 1000 accidents")
ax.legend(); plt.tight_layout()
save(fig, "fig02_de_severity_by_roadtype")

# ── Fig 3: NL motorway annual trends ─────────────────────────────────────────
print("Fig 3: NL motorway annual trends")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].plot(df_nl_annual["year"], df_nl_annual["total"],
             marker="o", color="#2a9d8f", linewidth=2, label="Total")
axes[0].plot(df_nl_annual["year"], df_nl_annual["serious"],
             marker="s", color="#e9c46a", linewidth=2, label="Serious injury")
axes[0].plot(df_nl_annual["year"], df_nl_annual["fatal"],
             marker="^", color="crimson", linewidth=2, label="Fatal")
axes[0].set_title("Motorway accidents by severity"); axes[0].set_xlabel("Year")
axes[0].set_ylabel("Count"); axes[0].legend()

axes[1].plot(df_nl_annual["year"], df_nl_annual["severity_idx"] * 1000,
             marker="o", color="crimson", linewidth=2)
axes[1].set_title("Severity index (fatalities per 1000 accidents)")
axes[1].set_xlabel("Year"); axes[1].set_ylabel("Fatalities per 1000 accidents")

fig.suptitle("Netherlands motorway safety (BRON)", fontweight="bold", fontsize=13)
plt.tight_layout()
save(fig, "fig03_nl_motorway_trends")

# ── Fig 4: DE vs NL severity index comparison ─────────────────────────────────
print("Fig 4: DE vs NL severity index comparison")
fig, ax = plt.subplots(figsize=(11, 5))

for grp_name, grp in df_combined.groupby("group"):
    ax.plot(grp["year"], grp["severity_idx"] * 1000,
            marker="o", label=grp_name, linewidth=2,
            color=PALETTE.get(grp_name, "grey"))

ax.set_title("Severity index: fatalities per 1000 accidents — DE vs NL",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year"); ax.set_ylabel("Fatalities per 1000 accidents")
ax.legend(); plt.tight_layout()
save(fig, "fig04_de_vs_nl_severity_index")

# ── Fig 5: Summary bar chart ──────────────────────────────────────────────────
print("Fig 5: Summary bar chart")
common_years = set(df_ua["year"].unique()) & set(df_nl_annual["year"].unique())

means = {
    "DE: Unlimited\nAutobahn": (
        df_ua[df_ua["on_unlimited"] & df_ua["year"].isin(common_years)]["severity"] == "fatal"
    ).mean() * 1000,
    "DE: Limited\nAutobahn": (
        df_ua[df_ua["on_limited_mw"] & df_ua["year"].isin(common_years)]["severity"] == "fatal"
    ).mean() * 1000,
    "NL:\nMotorway": df_nl_annual[df_nl_annual["year"].isin(common_years)]["severity_idx"].mean() * 1000,
}

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(list(means.keys()), list(means.values()),
              color=["#e63946", "#457b9d", "#2a9d8f"], width=0.5, edgecolor="white")
ax.bar_label(bars, fmt="%.2f", padding=4, fontsize=12, fontweight="bold")
ax.set_title("Mean fatality rate comparison (per 1000 accidents)\nCommon years: "
             f"{min(common_years)}–{max(common_years)}", fontsize=13, fontweight="bold")
ax.set_ylabel("Fatalities per 1000 accidents")
ax.set_ylim(0, max(means.values()) * 1.35)
sns.despine(); plt.tight_layout()
save(fig, "fig05_summary_bar")

# ── Fig 6: Statistical test result ───────────────────────────────────────────
print("Fig 6: Annual rate ratio unlimited vs limited")

years = sorted(df_ua["year"].unique())
results = []
for yr in years:
    yr_data = df_ua[df_ua["year"] == yr]
    n_unl = (yr_data["on_unlimited"] & (yr_data["severity"] == "fatal")).sum()
    n_lim = (yr_data["on_limited_mw"] & (yr_data["severity"] == "fatal")).sum()
    tot_unl = yr_data["on_unlimited"].sum()
    tot_lim = yr_data["on_limited_mw"].sum()
    if tot_unl > 0 and tot_lim > 0 and n_lim > 0:
        results.append({
            "year": yr,
            "rate_unlimited": n_unl / tot_unl * 1000,
            "rate_limited": n_lim / tot_lim * 1000,
            "rate_ratio": (n_unl / tot_unl) / (n_lim / tot_lim),
        })
df_results = pd.DataFrame(results)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].plot(df_results["year"], df_results["rate_unlimited"],
             marker="o", color="#e63946", linewidth=2, label="Unlimited")
axes[0].plot(df_results["year"], df_results["rate_limited"],
             marker="s", color="#457b9d", linewidth=2, label="Speed-limited")
axes[0].set_title("Fatality rate: unlimited vs limited Autobahn")
axes[0].set_xlabel("Year"); axes[0].set_ylabel("Fatalities per 1000 accidents")
axes[0].legend()

axes[1].bar(df_results["year"], df_results["rate_ratio"], color="#f4a261")
axes[1].axhline(1.0, color="grey", linestyle="--", linewidth=1)
axes[1].set_title("Rate ratio (unlimited / limited)")
axes[1].set_xlabel("Year"); axes[1].set_ylabel("Rate ratio")

fig.suptitle("Unlimited vs speed-limited Autobahn: fatality rate comparison",
             fontweight="bold", fontsize=13)
plt.tight_layout()
save(fig, "fig06_rate_ratio_unlimited_vs_limited")

# ── Print statistical summary ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STATISTICAL SUMMARY")
print("=" * 60)

total_unl_fatal = int((df_ua["on_unlimited"] & (df_ua["severity"] == "fatal")).sum())
total_lim_fatal = int((df_ua["on_limited_mw"] & (df_ua["severity"] == "fatal")).sum())
total_unl_acc = int(df_ua["on_unlimited"].sum())
total_lim_acc = int(df_ua["on_limited_mw"].sum())

rate_unl = total_unl_fatal / total_unl_acc * 1000
rate_lim = total_lim_fatal / total_lim_acc * 1000
result = stats.poisson_means_test(total_unl_fatal, total_unl_acc, total_lim_fatal, total_lim_acc)

nl_rate = df_nl_annual[df_nl_annual["year"].isin(common_years)]["severity_idx"].mean() * 1000

print(f"\n  DE Unlimited Autobahn : {rate_unl:.3f} fatalities / 1000 accidents")
print(f"  DE Limited Autobahn   : {rate_lim:.3f} fatalities / 1000 accidents")
print(f"  NL Motorway (mean)    : {nl_rate:.3f} fatalities / 1000 accidents")
print(f"\n  DE unlimited vs limited:")
print(f"    Rate ratio   : {rate_unl/rate_lim:.3f}x")
print(f"    Poisson p    : {result.pvalue:.4f} ({'SIGNIFICANT' if result.pvalue < 0.05 else 'not significant'})")
print(f"\n  DE unlimited vs NL motorway:")
print(f"    Rate ratio   : {rate_unl/nl_rate:.3f}x")

print(f"\n  Figures saved to: {FIG_DIR.resolve()}")
print("\nDone.")
