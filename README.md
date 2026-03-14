# Autobahn Speed Safety Analysis

A data science investigation into whether unlimited-speed sections of the German Autobahn are disproportionately dangerous compared to speed-limited motorways.

## Research Questions

1. Do unlimited-speed Autobahn sections have higher accident rates (per km and per vehicle-km) than speed-limited sections?
2. How do German motorway accident rates compare to Dutch motorways (A-roads, max 100–130 km/h)?
3. Has the safety trend on unlimited-speed sections diverged from speed-limited sections over time?

## Setup

```bash
uv sync
pre-commit install
jupyter lab
```

## Project Structure

```
notebooks/          — Jupyter notebooks (run in order)
src/autobahn_safety/ — Reusable Python modules
data/raw/           — Raw downloaded data (gitignored)
data/processed/     — Cleaned/merged datasets (gitignored)
tests/              — Unit tests
```

## Data Sources

See [`data/README.md`](data/README.md) for full details, download instructions, and API references.

## Notebooks

| # | Notebook | Purpose |
|---|----------|---------|
| 01 | `01_data_acquisition.ipynb` | Download/fetch all datasets |
| 02 | `02_data_exploration.ipynb` | EDA and data quality checks |
| 03 | `03_germany_autobahn_analysis.ipynb` | Germany: unlimited vs limited sections |
| 04 | `04_netherlands_comparison.ipynb` | Netherlands motorway analysis |
| 05 | `05_comparative_analysis.ipynb` | DE vs NL comparative rates + conclusions |

## License

MIT © Dennis Bakhuis 2026
