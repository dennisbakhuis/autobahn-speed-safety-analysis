"""Data preprocessing and cleaning utilities."""

from __future__ import annotations

import pandas as pd


# Unfallatlas severity codes
UKATEGORIE_MAP: dict[int, str] = {
    1: "fatal",
    2: "serious_injury",
    3: "slight_injury",
}

# Unfallatlas accident type codes (UART)
UART_MAP: dict[int, str] = {
    1: "driving_accident",
    2: "turning_accident",
    3: "turning_crossing_accident",
    4: "crossing_accident",
    5: "accident_stationary_vehicle",
    6: "accident_pedestrian",
    7: "wildlife_obstacle_accident",
    8: "other",
    9: "other",
}

# Unfallatlas day of week codes
WEEKDAY_MAP: dict[int, str] = {
    1: "Sunday",
    2: "Monday",
    3: "Tuesday",
    4: "Wednesday",
    5: "Thursday",
    6: "Friday",
    7: "Saturday",
}


def clean_unfallatlas(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize raw Unfallatlas data.

    Standardizes column names, maps categorical codes to human-readable labels,
    and creates derived columns useful for analysis.

    Args:
        df: Raw Unfallatlas DataFrame (as loaded by load_unfallatlas).

    Returns:
        Cleaned DataFrame with added label columns.
    """
    df = df.copy()

    # Map severity
    if "UKATEGORIE" in df.columns:
        df["severity"] = df["UKATEGORIE"].map(UKATEGORIE_MAP)

    # Map accident type
    if "UART" in df.columns:
        df["accident_type"] = df["UART"].map(UART_MAP)

    # Map weekday
    if "UWOCHENTAG" in df.columns:
        df["weekday"] = df["UWOCHENTAG"].map(WEEKDAY_MAP)

    # Location type: INN_ORT = 0 → outside built-up area (Autobahn, Bundesstraße, etc.)
    # Note: INN_ORT is not present in all Unfallatlas years.
    # Road type classification is done via spatial join with OSM in notebook 03.
    if "INN_ORT" in df.columns:
        df["outside_built_up_area"] = df["INN_ORT"] == 0

    # Rename coordinates for clarity
    coord_map = {"XGCSWGS84": "lon", "YGCSWGS84": "lat"}
    df = df.rename(columns={k: v for k, v in coord_map.items() if k in df.columns})

    # Parse coordinates to float (German CSVs use comma as decimal separator)
    # Check for both legacy object dtype and pandas 2+/3+ StringDtype
    for col in ("lon", "lat"):
        if col in df.columns and not pd.api.types.is_float_dtype(df[col]):
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            )

    return df


def normalize_to_rate(
    count: pd.Series,
    exposure: pd.Series,
    scale: float = 1e9,
) -> pd.Series:
    """Normalize accident counts to a rate per unit of exposure.

    Args:
        count: Accident or fatality counts.
        exposure: Exposure measure (e.g., vehicle-kilometres).
        scale: Output scaling factor (default: per billion vehicle-km).

    Returns:
        Rate series (same index as inputs).
    """
    return (count / exposure) * scale


def filter_autobahn(df: pd.DataFrame) -> pd.DataFrame:
    """Filter Unfallatlas data to likely Autobahn accidents.

    Uses available fields as proxies: outside built-up area, and where
    road class fields are present (STRASSE column naming Autobahn).

    Note:
        Unfallatlas does not always include an explicit road-class field.
        For more precise filtering, do a spatial join with an OSM Autobahn
        layer (see notebook 03 for the spatial approach).

    Args:
        df: Cleaned Unfallatlas DataFrame.

    Returns:
        Filtered DataFrame.
    """
    if "STRASSE" in df.columns:
        # Road names starting with 'A ' or 'BAB' typically denote Autobahn
        mask = df["STRASSE"].str.match(r"^(A\s+\d|BAB)", na=False)
        return df[mask].copy()

    # Fallback: outside built-up area only
    if "outside_built_up_area" in df.columns:
        return df[df["outside_built_up_area"]].copy()

    return df
