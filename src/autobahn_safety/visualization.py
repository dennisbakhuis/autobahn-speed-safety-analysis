"""Reusable visualization utilities for accident rate analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns


# Consistent color palette for groups
PALETTE: dict[str, str] = {
    "Germany (unlimited)": "#e63946",
    "Germany (limited)": "#457b9d",
    "Netherlands": "#2a9d8f",
    "Germany (Autobahn)": "#e63946",
    "Germany (Bundesstraße)": "#f4a261",
}


def plot_rate_trend(
    df: pd.DataFrame,
    *,
    x_col: str = "year",
    y_col: str = "rate",
    group_col: str = "group",
    title: str = "Accident/Fatality Rate Trend",
    ylabel: str = "Rate per billion vehicle-km",
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot accident or fatality rate trends over time, grouped by road type.

    Args:
        df: DataFrame with year, rate, and group columns.
        x_col: Column for x-axis (default: 'year').
        y_col: Column for y-axis rate values.
        group_col: Column used for grouping/coloring lines.
        title: Plot title.
        ylabel: Y-axis label.
        output_path: If provided, save the figure to this path.

    Returns:
        Matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x=x_col,
        y=y_col,
        hue=group_col,
        palette=PALETTE,
        ax=ax,
        marker="o",
        linewidth=2,
    )
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.legend(title="Group", framealpha=0.9)
    sns.despine()
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig


def plot_rate_comparison(
    df: pd.DataFrame,
    *,
    x_col: str = "group",
    y_col: str = "rate",
    title: str = "Rate Comparison",
    ylabel: str = "Rate per billion vehicle-km",
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot a bar chart comparing rates across road type groups.

    Args:
        df: DataFrame with group and rate columns.
        x_col: Column for x-axis (categorical groups).
        y_col: Column for bar heights.
        title: Plot title.
        ylabel: Y-axis label.
        output_path: If provided, save the figure to this path.

    Returns:
        Matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [PALETTE.get(g, "#888888") for g in df[x_col]]
    bars = ax.bar(df[x_col], df[y_col], color=colors, edgecolor="white", linewidth=0.8, width=0.6)
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=10)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Group", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_ylim(0, df[y_col].max() * 1.2)
    sns.despine()
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig


def plot_severity_heatmap(
    df: pd.DataFrame,
    *,
    index_col: str = "year",
    columns_col: str = "group",
    values_col: str = "severity_index",
    title: str = "Severity Index (fatalities per accident)",
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot a heatmap of severity index over time and across groups.

    Args:
        df: DataFrame with year, group, and severity_index columns.
        index_col: Column to use as heatmap rows.
        columns_col: Column to use as heatmap columns.
        values_col: Column with numeric values.
        title: Plot title.
        output_path: If provided, save the figure to this path.

    Returns:
        Matplotlib Figure.
    """
    pivot = df.pivot(index=index_col, columns=columns_col, values=values_col)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", annot=True, fmt=".3f", linewidths=0.5)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig
