"""Tests for analysis.py."""

import math

import pandas as pd
import pytest

from autobahn_safety.analysis import (
    annual_rate_trend,
    compute_accident_rate,
    compute_fatality_rate,
    compare_rates,
    severity_index,
)


def test_compute_accident_rate_basic() -> None:
    assert compute_accident_rate(1000, 1e9) == pytest.approx(1000.0)


def test_compute_accident_rate_zero_exposure() -> None:
    assert math.isnan(compute_accident_rate(100, 0))


def test_compute_fatality_rate_basic() -> None:
    assert compute_fatality_rate(50, 1e9) == pytest.approx(50.0)


def test_compute_fatality_rate_zero_exposure() -> None:
    assert math.isnan(compute_fatality_rate(10, 0))


def test_compare_rates_returns_dict() -> None:
    result = compare_rates(1000, 1e10, 500, 1e10)
    assert "rate_a" in result
    assert "rate_b" in result
    assert "rate_ratio" in result
    assert "p_value" in result


def test_compare_rates_ratio() -> None:
    result = compare_rates(2000, 1e10, 1000, 1e10)
    assert result["rate_ratio"] == pytest.approx(2.0)


def test_annual_rate_trend() -> None:
    df = pd.DataFrame(
        {
            "year": [2018, 2019, 2020],
            "accidents": [1000, 950, 800],
            "vehicle_km": [1e10, 1e10, 9e9],
        }
    )
    result = annual_rate_trend(df, count_col="accidents", exposure_col="vehicle_km")
    assert "rate" in result.columns
    assert len(result) == 3


def test_severity_index() -> None:
    fatalities = pd.Series([10, 20, 15])
    total = pd.Series([100, 200, 150])
    si = severity_index(fatalities, total)
    assert all(si == pytest.approx(0.1))
