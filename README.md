# Bluestock Mutual Fund Analytics Capstone

This repository contains the complete end-to-end data pipeline, analytics engine, and interactive dashboard for the Bluestock Mutual Fund Analytics Capstone project.

## Project Overview

The objective of this project is to build a robust system for tracking, analyzing, and visualizing Mutual Fund performance. The system automatically fetches live Net Asset Values (NAV) from the AMFI API, cleans and normalizes the data, computes critical risk and performance metrics, and presents these insights through an interactive Streamlit web application.

### Key Features
- **Automated ETL**: Daily fetch of live NAVs, merged seamlessly with 5-year historical data.
- **Relational Data Warehouse**: A localized SQLite database (`bluestock_mf.db`) ensuring data integrity across dimension and fact tables.
- **Advanced Analytics**: Computation of trading-day annualized CAGR, Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Value at Risk (VaR), Conditional VaR, and Sector Concentration (HHI).
- **Interactive Dashboard**: A dynamic Streamlit frontend with Plotly visualizations, allowing users to filter by category, risk profile, and time horizon to map the Efficient Frontier.
- **Bonus Capabilities**: Monte Carlo NAV simulations, Portfolio Optimisation (Markowitz model), and an automated HTML Email Report generator.

---

## Directory Structure

```text
bluestock_mf_capstone/
├── app.py                     # Main Streamlit Dashboard Application
├── run_pipeline.py            # Master execution script for the data pipeline
├── data/                      # Raw inputs, processed outputs, and SQLite database
├── notebooks/                 # Jupyter notebooks for EDA and prototyping
├── reports/                   # Final PDF/Markdown reports and generated HTML reports
├── scripts/                   # Python modules for ETL, metrics, and automation
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Setup Instructions

### Prerequisites
Ensure you have Python 3.9+ installed. It is highly recommended to use a virtual environment.

### 1. Clone the Repository
```bash
git clone https://github.com/Subhasish-33/bluestock-mutual-fund-analytics.git
cd bluestock-mutual-fund-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: If `requirements.txt` is missing, standard libraries include `pandas`, `numpy`, `scipy`, `streamlit`, `plotly`, `sqlalchemy`, and `schedule`)*.

---

## How to Run the Pipeline

To rebuild the database from scratch and recalculate all metrics, run the master pipeline script:

```bash
python run_pipeline.py
```

This orchestrates the following sequential steps:
1. Data Ingestion & Cleaning
2. Loading to SQLite
3. Computation of basic and advanced metrics

To run the automated daily ETL scheduler (fetches live NAVs at 8:00 PM on weekdays):
```bash
python scripts/schedule_etl.py
```

---

## How to Open the Dashboard

The interactive dashboard is built with Streamlit. To launch it locally, run:

```bash
streamlit run app.py
```

This will automatically open your default web browser to `http://localhost:8501`. 

### Dashboard Navigation
- **Overview**: High-level KPI metrics and total AUM.
- **Fund Explorer**: Filter and view individual scheme details and historical NAV charts.
- **Performance**: Analyze risk vs return (CAGR vs Volatility) and view the Rolling Sharpe ratios.
- **Advanced Risk**: View Drawdowns, VaR, CVaR, and Sector Concentration metrics.

---

## Contributing
This is a capstone project submission and is not currently accepting pull requests.

## License
MIT License
