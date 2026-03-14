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


def download_unfallatlas(year: int, output_dir: Path, *, force: bool = False) -> Path:
    """Download and extract Unfallatlas CSV data for a given year.

    The Unfallatlas provides GPS-located individual accident records for all of
    Germany, published jointly by the Statistische Landesämter. Available from
    2016 onwards.

    Skips the download if the data file is already present, unless force=True.

    Args:
        year: The year to download (2016–2024 available).
        output_dir: Directory to save extracted files.
        force: Re-download even if data already exists (default: False).

    Returns:
        Path to the extracted data file.

    Raises:
        requests.HTTPError: If the download fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Skip if already downloaded (check for LinRef data file, either .csv or .txt)
    if not force:
        existing = [
            f for f in output_dir.rglob("*LinRef*")
            if f.suffix.lower() in (".csv", ".txt") and f.is_file()
        ]
        if existing:
            print(f"{year}: already downloaded ({existing[0].name})")
            return existing[0]

    url = f"https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/Unfallorte{year}_EPSG25832_CSV.zip"
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
    data_files = [
        f for f in output_dir.rglob("*LinRef*")
        if f.suffix.lower() in (".csv", ".txt") and f.is_file()
    ]
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
        # Try UTF-8 with BOM first (some years), fall back to latin-1
        try:
            df = pd.read_csv(candidates[0], sep=";", encoding="utf-8-sig", low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(candidates[0], sep=";", encoding="latin-1", low_memory=False)

        # Normalise column names: strip whitespace and BOM remnants
        df.columns = df.columns.str.strip().str.lstrip("\ufeff")

        df["year"] = year
        frames.append(df)
    if not frames:
        return pd.DataFrame()

    # Concat across years — keep only the common core columns to avoid NaN explosion
    # from schema differences between years
    core_cols = [
        "ULAND", "UREGBEZ", "UKREIS", "UGEMEINDE",
        "UJAHR", "UMONAT", "USTUNDE", "UWOCHENTAG",
        "UKATEGORIE", "UART", "UTYP1", "ULICHTVERH",
        "IstRad", "IstPKW", "IstFuss", "IstKrad", "IstGkfz",
        "LINREFX", "LINREFY", "XGCSWGS84", "YGCSWGS84",
        "year",
    ]
    available = [c for c in core_cols if any(c in df.columns for df in frames)]
    trimmed = []
    for df in frames:
        cols = [c for c in available if c in df.columns]
        trimmed.append(df[cols])
    return pd.concat(trimmed, ignore_index=True)


def download_destatis_timeseries(output_dir: Path, *, force: bool = False) -> Path:
    """Download the Destatis accident statistics time series Excel workbook.

    This replaces the old GENESIS-Online REST API (which has been decommissioned).
    Downloads the official "Statistischer Bericht Verkehrsunfälle — Zeitreihen" Excel
    publication directly from destatis.de.

    The workbook contains all road-type breakdowns including Autobahn (sheet 3.1_(4)).
    No registration required.

    Args:
        output_dir: Directory to save the Excel file.
        force: Re-download even if file already exists (default: False).

    Returns:
        Path to the downloaded Excel file.

    Raises:
        requests.HTTPError: If the download fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    out_path = output_dir / "destatis_verkehrsunfaelle_zeitreihen.xlsx"
    if not force and out_path.exists():
        print(f"Destatis timeseries: already downloaded ({out_path.name})")
        return out_path

    url = (
        "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Verkehrsunfaelle/"
        "Publikationen/Downloads-Verkehrsunfaelle/"
        "verkehrsunfaelle-zeitreihen-xlsx-5462403.xlsx?__blob=publicationFile&v=19"
    )
    print("Downloading Destatis accident time series (~36 MB)...")
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    with open(out_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc="Destatis timeseries") as pbar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))

    print(f"Saved to {out_path}")
    return out_path


def load_destatis_autobahn(xlsx_path: Path) -> pd.DataFrame:
    """Load Autobahn accident statistics from the Destatis time series workbook.

    Reads sheet '3.1_(4)' which contains accidents on motorways (Autobahnen)
    going back to the 1950s. Returns a clean long-format DataFrame.

    Args:
        xlsx_path: Path to the destatis Zeitreihen Excel file.

    Returns:
        DataFrame with columns: year, accidents_total, accidents_personal_injury,
        accidents_fatal, killed, injured.
    """
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb["3.1_(4)"]

    rows = list(ws.iter_rows(values_only=True))

    # Find the header row (contains year-like integer values in the first column)
    data_rows = []
    for row in rows:
        first = row[0]
        if isinstance(first, (int, float)) and 1950 <= int(first) <= 2030:
            data_rows.append(row)

    if not data_rows:
        raise ValueError("Could not find data rows in sheet 3.1_(4)")

    # Column layout (Autobahn sheet):
    # 0: year | 1: accidents_total | 2: accidents_personal_injury
    # 3: accidents_fatal (with killed) | 4: accidents_injury_only
    # 5: schwerwiegende_sachschaden | 6+: Verunglückte breakdown
    records = []
    for row in data_rows:
        def _int(v):  # noqa: E306
            try:
                return int(v) if v not in (None, ".", "") else None
            except (ValueError, TypeError):
                return None

        records.append({
            "year": _int(row[0]),
            "accidents_total": _int(row[1]),
            "accidents_personal_injury": _int(row[2]),
            "accidents_fatal": _int(row[3]),
        })

    df = pd.DataFrame(records).dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df.sort_values("year").reset_index(drop=True)


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
