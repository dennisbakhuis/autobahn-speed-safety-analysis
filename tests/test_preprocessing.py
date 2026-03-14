"""Tests for preprocessing.py."""

import pandas as pd
import pytest

from autobahn_safety.preprocessing import (
    clean_unfallatlas,
    normalize_to_rate,
    filter_autobahn,
)


@pytest.fixture()
def raw_unfallatlas_df() -> pd.DataFrame:
    """Minimal mock of a raw Unfallatlas DataFrame."""
    return pd.DataFrame(
        {
            "UKATEGORIE": [1, 2, 3, 1],
            "UART": [1, 2, 3, 7],
            "UWOCHENTAG": [2, 4, 6, 1],
            "XGCSWGS84": ["13,404954", "13,500000", "52,100000", "9,993682"],
            "YGCSWGS84": ["52,520008", "52,600000", "13,200000", "53,550341"],
            "year": [2020, 2020, 2020, 2021],
        }
    )


def test_clean_unfallatlas_severity(raw_unfallatlas_df: pd.DataFrame) -> None:
    df = clean_unfallatlas(raw_unfallatlas_df)
    assert "severity" in df.columns
    assert df["severity"].iloc[0] == "fatal"
    assert df["severity"].iloc[1] == "serious_injury"
    assert df["severity"].iloc[2] == "slight_injury"


def test_clean_unfallatlas_coordinates(raw_unfallatlas_df: pd.DataFrame) -> None:
    df = clean_unfallatlas(raw_unfallatlas_df)
    assert "lon" in df.columns
    assert "lat" in df.columns
    assert df["lon"].dtype == float


def test_clean_unfallatlas_weekday(raw_unfallatlas_df: pd.DataFrame) -> None:
    df = clean_unfallatlas(raw_unfallatlas_df)
    assert "weekday" in df.columns
    assert df["weekday"].iloc[0] == "Monday"


def test_clean_unfallatlas_outside_built_up_when_inn_ort_present() -> None:
    """INN_ORT is optional (not present in all years); column created only when available."""
    df_with = pd.DataFrame({"INN_ORT": [0, 0, 1], "XGCSWGS84": ["13,4", "13,5", "13,6"],
                            "YGCSWGS84": ["52,5", "52,6", "52,7"], "year": [2020, 2020, 2020]})
    cleaned = clean_unfallatlas(df_with)
    assert "outside_built_up_area" in cleaned.columns
    assert cleaned["outside_built_up_area"].iloc[0] == True  # noqa: E712
    assert cleaned["outside_built_up_area"].iloc[2] == False  # noqa: E712

    df_without = pd.DataFrame({"XGCSWGS84": ["13,4"], "YGCSWGS84": ["52,5"], "year": [2020]})
    cleaned_no = clean_unfallatlas(df_without)
    assert "outside_built_up_area" not in cleaned_no.columns


def test_normalize_to_rate() -> None:
    count = pd.Series([100, 200, 300])
    exposure = pd.Series([1e9, 2e9, 3e9])
    rate = normalize_to_rate(count, exposure)
    expected = pd.Series([100.0, 100.0, 100.0])
    pd.testing.assert_series_equal(rate, expected)


def test_filter_autobahn_by_street_name() -> None:
    df = pd.DataFrame(
        {
            "STRASSE": ["A 9", "B 12", "A 81", "Kreisstraße 5"],
            "year": [2020, 2020, 2020, 2020],
        }
    )
    result = filter_autobahn(df)
    assert len(result) == 2
    assert all(result["STRASSE"].str.startswith("A "))
