# Bluestock Mutual Fund Analytics - Scripts Directory

This directory contains all the Python modules and executable scripts that power the data pipeline, metric computation, and background tasks for the capstone project.

## Overview of Scripts

- **`data_ingestion.py` / `live_nav_fetch.py`**: Handles API connections to AMFI to retrieve live daily NAV data and cleans historical NAV datasets.
- **`load_to_sqlite.py`**: Manages the ETL load phase, creating tables and inserting processed pandas DataFrames into the local `bluestock_mf.db` SQLite database.
- **`compute_metrics.py`**: Computes core performance and risk metrics (CAGR, Annualized Volatility, Sharpe Ratio, Sortino Ratio).
- **`compute_var_cvar.py`**: Calculates Value at Risk (VaR) and Conditional Value at Risk (CVaR) using historical simulations.
- **`compute_sector_hhi.py`**: Calculates the Herfindahl-Hirschman Index to measure portfolio sector concentration.
- **`compute_cohort_analysis.py` / `compute_sip_continuity.py`**: Analyzes investor transaction patterns and SIP retention drop-offs.
- **`monte_carlo_nav.py`**: Bonus challenge script executing Geometric Brownian Motion simulations for 5-year NAV projections.
- **`portfolio_optimisation.py`**: Bonus challenge script generating the Markowitz Efficient Frontier.
- **`schedule_etl.py`**: Wrapper script using the `schedule` library to automatically trigger data ingestion at 8:00 PM on weekdays.
- **`email_report_generator.py`**: Generates a professional HTML performance report using Jinja2 templates.
- **`generate_presentation.py`**: Programmatically generates the 12-slide final presentation deck using `python-pptx`.

## Usage
Most of these scripts are orchestrated sequentially by the master `run_pipeline.py` script located in the root directory. However, you can run them individually for debugging:

```bash
python scripts/compute_metrics.py
```
