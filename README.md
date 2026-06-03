# Bluestock — Mutual Fund Analytics
**Capstone Project | Data Analyst Internship 2026**

An end-to-end data analytics and business intelligence pipeline built to ingest, clean, store, and analyze mutual fund Net Asset Values (NAV), fund performances, and investor transactions for Bluestock Fintech.

---

## 🚀 Project Overview

This capstone project transforms raw industry data and investor logs into a fully structured relational database (SQLite) capable of powering advanced financial models and interactive BI dashboards. The project includes:
- Automated ingestion of multi-source raw files.
- Rigorous data cleaning, validation, and imputation.
- A fully normalized relational database schema with strict foreign key constraints.
- Optimized analytical queries for mutual fund performance metrics (e.g., Sharpe Ratio, Alpha, Beta) and investor risk profiling.

---

## 🛠️ Tech Stack

- **Data Processing:** Python, Pandas, NumPy, Jupyter Notebooks
- **Storage & Relational Database:** SQLite, SQLite3, SQL (DDL, DML)
- **External API:** `mfapi.in` (for live NAV fetching)

---

## 📁 Project Directory Structure

```
bluestock_mf_capstone/
├── README.md                      # Project documentation and guide
├── data_dictionary.md             # Schema documentation for all 8 database tables
├── data/
│   ├── raw/                       # Raw source CSV files (not tracked in Git)
│   ├── processed/                 # Cleaned, standardized CSV datasets
│   │   ├── clean_nav.csv          # Cleaned daily NAV history
│   │   ├── clean_performance.csv  # Cleaned scheme performance snapshot
│   │   └── clean_transactions.csv # Cleaned investor transaction log
│   └── db/
│       └── bluestock_mf.db        # The production SQLite database (97,782 records)
├── notebooks/
│   ├── 01_data_ingestion.ipynb    # Phase 1: Ingestion validation
│   ├── 02_data_cleaning.ipynb     # Phase 2: Cleaning NAV history & forward-fill
│   ├── 03_clean_transactions.ipynb# Phase 2: Cleaning investor transaction records
│   ├── 04_clean_performance.ipynb # Phase 2: Cleaning scheme performance & auditing
│   ├── 03_eda_analysis.ipynb      # Phase 3: Exploratory Data Analysis (Pending)
│   └── 04_performance_analytics.ipynb # Phase 4: Financial metrics & modeling (Pending)
├── scripts/
│   ├── load_to_sqlite.py          # ETL Script to recreate and populate the database
│   ├── live_nav_fetch.py          # Live NAV retrieval API client
│   └── generate_scheme_navs.py    # Utility to match schemes with NAV datasets
└── sql/
    ├── schema.sql                 # Database Schema (8 Tables, 3 Views, 18 Indexes)
    └── queries.sql                # 10 BI and analytical SQL queries
```

---

## 📅 Roadmap & Progress

### ✅ Day 1: Ingestion & Live NAV Fetching
- Consolidated **20 raw NAV history CSV files** (55,397 records).
- Implemented and verified mappings between `fund_master` and NAV records using AMFI codes.
- Integrated with `mfapi.in` API to fetch real-time NAV prices dynamically.

### ✅ Day 2: Data Cleaning, Schema Design & SQLite Integration
- **Advanced Data Cleaning:**
  - Standardized datetime formats across transaction logs, performance files, and NAV tables.
  - Imputed calendar gaps (weekends/holidays) in NAV series using forward-fill (`ffill`).
  - Added computed fields like `daily_return` for each scheme.
  - Resolved inconsistent transactions, filtered out-of-bounds metrics, and added compliance audit flags (e.g. `negative_sharpe_flag`, `expense_ratio_out_of_range_flag`).
- **Database Architecture & Loading:**
  - Designed and built a normalized schema with 8 tables, 3 BI-focused views, and 18 indexes for search speed optimization.
  - Developed `scripts/load_to_sqlite.py` to perform full schema setups and load **97,782 total rows** with active foreign key enforcement (`PRAGMA foreign_keys = ON;`).
  - Created a comprehensive [Data Dictionary](file:///Users/subhasish/bluestock_mf_capstone/data_dictionary.md) specifying constraints, keys, and column details.
- **Analytical Insights:**
  - Designed 10 working analytical queries in `sql/queries.sql` to retrieve:
    1. Top 5 Funds by Assets Under Management (AUM)
    2. Average NAV Per Month (Industry-Wide)
    3. Year-on-Year growth rates for SIP inflows
    4. Transaction counts and volume by Indian state
    5. Low-cost mutual fund schemes (Expense Ratio < 1%)
    6. Top 5 Funds by 3-Year Risk-Adjusted Returns (Sharpe Ratio)
    7. Monthly SIP vs. Lumpsum vs. Redemption transaction counts & values
    8. Fund Performance vs. Benchmark (Alpha / Beta analysis)
    9. Real NAV-based 1-Year rolling return calculations
    10. KYC-Pending investor SIP risk exposure

---

## ⚙️ Setup and Execution

### 1. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Rerun the ETL Pipeline
To rebuild the SQLite database schema and reload all cleaned datasets:
```bash
python scripts/load_to_sqlite.py
```

### 3. Run Analytical Queries
You can run the SQL queries using the SQLite command-line interface:
```bash
sqlite3 data/db/bluestock_mf.db < sql/queries.sql
```
Alternatively, open the database using any SQL client (such as DBeaver or DB Browser for SQLite) to execute queries interactively.
