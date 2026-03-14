"""Data loading utilities for the Autobahn Speed Safety Analysis project."""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm


def download_unfallatlas(year: int, output_dir: Path) -> Path:
    """Download and extract Unfallatlas CSV data for a given year.

    The Unfallatlas provides GPS-located individual accident records for all of
    Germany, published jointly by the Statistische Landesämter. Available from
    2016 onwards.

    Args:
        year: The year to download (2016–2024 available).
        output_dir: Directory to save extracted files.

    Returns:
        Path to the directory containing extracted files.

    Raises:
        requests.HTTPError: If the download fails.
    """
    url = f"https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/Unfallorte{year}_EPSG25832_CSV.zip"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    buf = io.BytesIO()
    with tqdm(total=total, unit="B", unit_scale=True, desc=f"Unfallatlas {year}") as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            buf.write(chunk)
            pbar.update(len(chunk))

    buf.seek(0)
    with zipfile.ZipFile(buf) as zf:
        zf.extractall(output_dir)

    # Find the actual data file (structure varies by year: flat CSV, subdir CSV, or subdir TXT)
    data_files = list(output_dir.rglob("*LinRef*"))
    data_files = [f for f in data_files if f.suffix.lower() in (".csv", ".txt") and f.is_file()]
    return data_files[0] if data_files else output_dir


def load_unfallatlas(data_dir: Path, years: list[int]) -> pd.DataFrame:
    """Load and concatenate Unfallatlas CSV files for multiple years.

    Args:
        data_dir: Directory containing per-year extracted CSV files.
        years: List of years to load.

    Returns:
        Concatenated DataFrame with an added 'year' column.
    """
    frames = []
    for year in years:
        year_dir = Path(data_dir) / str(year)
        # Search recursively for the LinRef data file (extension varies: .csv or .txt)
        candidates = list(year_dir.rglob("*LinRef*")) if year_dir.exists() else []
        candidates = [f for f in candidates if f.suffix.lower() in (".csv", ".txt") and f.is_file()]
        if not candidates:
            print(f"Warning: no Unfallatlas file found for {year}")
            continue
        df = pd.read_csv(candidates[0], sep=";", encoding="latin-1", low_memory=False)
        df["year"] = year
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def fetch_destatis_genesis(
    table_id: str,
    *,
    start_year: int = 2010,
    end_year: int = 2023,
) -> pd.DataFrame:
    """Fetch aggregated accident statistics from Destatis GENESIS-Online API.

    Requires free registration at https://www-genesis.destatis.de/
    Set DESTATIS_USERNAME and DESTATIS_PASSWORD in your .env file.

    Useful tables:
        - "46241-0023": Accidents by category and location type (Autobahn, etc.)
        - "46241-0031": Accidents on motorways specifically
        - "46241-0010": Overview by year

    Args:
        table_id: GENESIS table ID (e.g. "46241-0023").
        start_year: Start of time series.
        end_year: End of time series.

    Returns:
        DataFrame with the requested table data.

    Raises:
        requests.HTTPError: If the API request fails.
        ValueError: If credentials are not set.
    """
    load_dotenv()
    username = os.getenv("DESTATIS_USERNAME", "")
    password = os.getenv("DESTATIS_PASSWORD", "")
    if not username or not password:
        raise ValueError(
            "Set DESTATIS_USERNAME and DESTATIS_PASSWORD in .env — "
            "register free at https://www-genesis.destatis.de/"
        )

    base_url = "https://www-genesis.destatis.de/api/rest/2020"
    params = {
        "username": username,
        "password": password,
        "name": table_id,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "language": "en",
    }
    resp = requests.get(f"{base_url}/data/tablefile", params=params, timeout=60)
    resp.raise_for_status()

    # GENESIS returns semicolon-separated CSV with metadata rows at the top
    return pd.read_csv(io.StringIO(resp.text), sep=";", skiprows=5, encoding="utf-8")


def fetch_cbs_odata(
    dataset_id: str,
    *,
    filter_expr: str | None = None,
    select_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Fetch a CBS (Statistics Netherlands) OData dataset.

    No authentication required. Automatically handles pagination.

    Useful datasets:
        - "71738NED": casualties by road type (verkeersslachtoffers naar wegtype)
        - "81395NED": traffic accidents overview

    Args:
        dataset_id: CBS dataset ID (e.g. "71738NED").
        filter_expr: Optional OData $filter expression.
        select_cols: Optional list of columns to select ($select).

    Returns:
        DataFrame with all records from the dataset.

    Raises:
        requests.HTTPError: If any page request fails.
    """
    base_url = f"https://opendata.cbs.nl/ODataApi/odata/{dataset_id}/UntypedDataSet"
    params: dict[str, str] = {}
    if filter_expr:
        params["$filter"] = filter_expr
    if select_cols:
        params["$select"] = ",".join(select_cols)

    all_records: list[dict] = []
    url: str | None = base_url

    while url:
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        all_records.extend(data.get("value", []))
        url = data.get("odata.nextLink")
        params = {}  # subsequent pages embed params in the nextLink URL

    return pd.DataFrame(all_records)
