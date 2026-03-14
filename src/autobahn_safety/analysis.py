"""Statistical analysis utilities for accident rate comparison."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def compute_accident_rate(
    accidents: int | float,
    vehicle_km: float,
    scale: float = 1e9,
) -> float:
    """Compute accident rate per unit of vehicle exposure.

    Args:
        accidents: Number of accidents.
        vehicle_km: Total vehicle-kilometres travelled.
        scale: Output denominator (default: 1e9 = per billion veh-km).

    Returns:
        Accident rate, or NaN if exposure is zero.
    """
    if vehicle_km == 0:
        return float("nan")
    return (accidents / vehicle_km) * scale


def compute_fatality_rate(
    fatalities: int | float,
    vehicle_km: float,
    scale: float = 1e9,
) -> float:
    """Compute fatality rate per unit of vehicle exposure.

    Args:
        fatalities: Number of fatalities.
        vehicle_km: Total vehicle-kilometres travelled.
        scale: Output denominator (default: 1e9 = per billion veh-km).

    Returns:
        Fatality rate, or NaN if exposure is zero.
    """
    if vehicle_km == 0:
        return float("nan")
    return (fatalities / vehicle_km) * scale


def compare_rates(
    count_a: int,
    exposure_a: float,
    count_b: int,
    exposure_b: float,
    scale: float = 1e9,
) -> dict[str, float]:
    """Compare two Poisson accident rates using a rate ratio test.

    Tests whether the accident rate in group A differs significantly
    from group B using a Poisson means test.

    Args:
        count_a: Accident count in group A (e.g., unlimited Autobahn).
        exposure_a: Exposure (vehicle-km) in group A.
        count_b: Accident count in group B (e.g., limited Autobahn).
        exposure_b: Exposure (vehicle-km) in group B.
        scale: Rate scaling factor (default: per billion veh-km).

    Returns:
        Dict with keys: rate_a, rate_b, rate_ratio, p_value.
    """
    rate_a = (count_a / exposure_a) * scale if exposure_a else float("nan")
    rate_b = (count_b / exposure_b) * scale if exposure_b else float("nan")
    rate_ratio = rate_a / rate_b if rate_b else float("nan")

    result = stats.poisson_means_test(count_a, exposure_a, count_b, exposure_b)

    return {
        "rate_a": rate_a,
        "rate_b": rate_b,
        "rate_ratio": rate_ratio,
        "p_value": result.pvalue,
    }


def annual_rate_trend(
    df: pd.DataFrame,
    *,
    count_col: str,
    exposure_col: str,
    year_col: str = "year",
    scale: float = 1e9,
) -> pd.DataFrame:
    """Compute accident/fatality rate per year from a grouped DataFrame.

    Args:
        df: DataFrame with yearly aggregated counts and exposure.
        count_col: Column name for accident/fatality counts.
        exposure_col: Column name for vehicle-km exposure.
        year_col: Column name for the year.
        scale: Rate scaling factor.

    Returns:
        DataFrame with columns [year, count, exposure, rate].
    """
    result = df[[year_col, count_col, exposure_col]].copy()
    result["rate"] = (result[count_col] / result[exposure_col]) * scale
    return result.rename(columns={count_col: "count", exposure_col: "exposure"})


def severity_index(fatalities: pd.Series, total_accidents: pd.Series) -> pd.Series:
    """Compute the severity index (fatalities per accident).

    Args:
        fatalities: Fatality counts.
        total_accidents: Total accident counts (all severities).

    Returns:
        Severity index series (values between 0 and 1).
    """
    return fatalities / total_accidents.replace(0, np.nan)
