# Data Sources

All raw data lives in `data/raw/` (gitignored). Download instructions below.

---

## Germany

### 1. Unfallatlas — Individual GPS-level accident data

- **Provider:** Statistisches Bundesamt + Statistische Landesämter
- **Coverage:** 2016–present, all of Germany
- **Granularity:** Individual accident records with GPS coordinates
- **Download:** https://unfallatlas.statistikportal.de/ → "Download" tab → CSV ZIP per year
- **Direct URL pattern:** `https://unfallatlas.statistikportal.de/_data/Unfallorte{YEAR}_EPSG25832_CSV.zip`
- **Key fields:**
  - `UKATEGORIE` — severity (1=fatal, 2=serious injury, 3=slight injury)
  - `UART` — accident type
  - `UTYP1` — collision type
  - `INN_ORT` — inside (1) / outside (0) built-up area
  - `ULICHTVERH` — lighting conditions
  - `UWOCHENTAG` — day of week
  - `USTUNDE` — hour of day
  - `XGCSWGS84`, `YGCSWGS84` — WGS84 coordinates (lon, lat)
- **Local path:** `data/raw/germany/unfallatlas/`
- **Note:** Road class (Autobahn vs Bundesstraße) must be inferred from spatial join with road network or from supplementary fields. Speed limit data is not directly encoded — use road type as proxy.

### 2. Destatis GENESIS-Online — Aggregated accident statistics

- **Provider:** Federal Statistical Office (Destatis)
- **Coverage:** 1991–present, annual
- **Granularity:** Aggregated by road type, severity, state
- **Tables of interest:**
  - `46241-0023` — accidents by category and location type (Autobahn, Bundesstraße, Kreisstraße, etc.)
  - `46241-0031` — accidents on motorways (Autobahn) specifically
  - `46241-0010` — overview by year
- **API:** https://www-genesis.destatis.de/api/ (free registration required)
- **Web:** https://www-genesis.destatis.de/genesis/online
- **Credentials:** Set `DESTATIS_USERNAME` and `DESTATIS_PASSWORD` in `.env`
- **Local path:** `data/raw/germany/destatis/`

### 3. BASt — Traffic volume data (vehicle-km)

- **Provider:** Bundesanstalt für Straßenwesen (Federal Highway Research Institute)
- **Purpose:** Exposure data (vehicle-km by road type) — essential for computing accident rates
- **Download:** https://www.bast.de/DE/Statistik/Unfaelle/Unfalldaten.html
  - "Straßenverkehrsunfälle nach Straßenklassen" Excel files
- **Alternatively:** Kraftfahrt-Bundesamt (KBA) traffic performance data
- **Local path:** `data/raw/germany/bast/`

---

## Netherlands

### 4. CBS OData API — Road accident casualties by road type

- **Provider:** CBS (Statistics Netherlands)
- **Coverage:** 2000–present, annual
- **Granularity:** Aggregated by road type, severity, region, year
- **API:** https://opendata.cbs.nl/ODataApi/odata/{DATASET_ID}/
- **Relevant datasets:**
  - Search: https://opendata.cbs.nl/dataportaal/portal.html#/CBS/en (search "traffic accidents")
  - `71738NED` — verkeersslachtoffers naar weg type (casualties by road type)
  - `81395NED` — verkeersongevallen (traffic accidents)
- **No registration required**
- **Local path:** `data/raw/netherlands/cbs/`

### 5. BRON — Individual accident records (Netherlands)

- **Provider:** CBS / SWOV / Rijkswaterstaat
- **Full name:** Bestand geRegistreerde Ongevallen in Nederland
- **Coverage:** 1996–present, individual accident records
- **Download:** https://data.overheid.nl (search "BRON verkeersongevallen")
  - Or: https://www.swov.nl/feiten-cijfers/bronnen-en-methoden/bron (request via SWOV)
- **Key fields:** road type, speed limit, severity, coordinates, year
- **Local path:** `data/raw/netherlands/bron/`

### 6. Rijkswaterstaat NDW — Traffic volume (vehicle-km)

- **Provider:** Rijkswaterstaat / Nationaal Dataportaal Wegverkeer
- **Purpose:** Exposure data for rate calculations
- **Download:** https://www.rijkswaterstaat.nl/wegen/wegbeheer/verkeersgegevens
  - Or: https://ndw.nu/en/
- **Local path:** `data/raw/netherlands/ndw/`

---

## Comparative / EU

### 7. ERSO / CARE Database — EU-standardized road safety statistics

- **Provider:** European Commission / European Road Safety Observatory
- **Coverage:** All EU member states, annual, 1991–present
- **Purpose:** Direct standardized comparison DE vs NL by road type
- **Access:** https://road-safety.transport.ec.europa.eu/
  - Statistical reports, country profiles, downloadable tables
- **Local path:** `data/raw/eu/erso/`

### 8. ETSC PIN — European performance index

- **Provider:** European Transport Safety Council
- **Coverage:** EU member states, annual road safety benchmark
- **Download:** https://etsc.eu/eurorap-pin/
- **Local path:** `data/raw/eu/etsc/`

---

## Key Metrics to Derive

| Metric | Formula | Unit |
|--------|---------|------|
| Accident rate | accidents / vehicle-km | per billion veh-km |
| Fatality rate | fatalities / vehicle-km | per billion veh-km |
| Accident density | accidents / road-km | per km per year |
| Severity index | fatalities / total accidents | ratio |
