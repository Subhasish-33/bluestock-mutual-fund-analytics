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
- Advanced risk analytics: Historical VaR, CVaR, Rolling Sharpe Ratio, Sector HHI concentration.
- Investor behaviour analytics: Cohort analysis, SIP continuity flagging, fund recommendation engine.

---

## 🛠️ Tech Stack

- **Data Processing:** Python, Pandas, NumPy, Jupyter Notebooks
- **Storage & Relational Database:** SQLite, SQLite3, SQL (DDL, DML)
- **Visualization:** Matplotlib (charts, rolling metrics, HHI bar charts)
- **BI Dashboard:** Tableau Public (interactive 4-page dashboard)
- **Risk Metrics:** Historical VaR, CVaR (Expected Shortfall), HHI, Rolling Sharpe
- **External API:** `mfapi.in` (for live NAV fetching)

---

## 📁 Project Directory Structure

```
bluestock_mf_capstone/
├── README.md                          # Project documentation and guide
├── data_dictionary.md                 # Schema documentation for all 8 database tables
├── data/
│   ├── raw/                           # Raw source CSV files (not tracked in Git)
│   ├── processed/                     # Cleaned, standardized CSV datasets
│   │   ├── clean_nav.csv              # Cleaned daily NAV history (64K rows, 40 funds)
│   │   ├── clean_performance.csv      # Cleaned scheme performance snapshot
│   │   ├── clean_transactions.csv     # Cleaned investor transaction log (32K rows)
│   │   ├── fund_scorecard.csv         # Composite fund ranking (Day 4)
│   │   ├── var_cvar_report.csv        # Historical VaR 95% & CVaR per fund (Day 6)
│   │   ├── cohort_analysis.csv        # Investor cohort SIP metrics by year (Day 6)
│   │   ├── sip_continuity.csv         # SIP gap analysis & at-risk flags (Day 6)
│   │   └── sector_hhi.csv             # Sector HHI concentration per equity fund (Day 6)
│   └── db/
│       └── bluestock_mf.db            # The production SQLite database (97,782 records)
├── notebooks/
│   ├── 01_data_ingestion.ipynb        # Phase 1: Ingestion validation
│   ├── 02_data_cleaning.ipynb         # Phase 2: Cleaning NAV history & forward-fill
│   ├── 03_clean_transactions.ipynb    # Phase 2: Cleaning investor transaction records
│   ├── 04_clean_performance.ipynb     # Phase 2: Cleaning scheme performance & auditing
│   ├── 03_eda_analysis.ipynb          # Phase 3: Exploratory Data Analysis
│   ├── Performance_Analytics.ipynb    # Phase 4: Financial metrics & modeling
│   ├── Advanced_Analytics.ipynb       # Phase 6: Advanced analytics summary (Day 6) ⭐
│   └── reports/
│       ├── rolling_sharpe_chart.png   # Rolling 90-day Sharpe for top 5 funds (Day 6)
│       └── sector_hhi_chart.png       # Sector HHI concentration bar chart (Day 6)
├── reports/
│   ├── figures/                       # Exported PNG charts from EDA
│   ├── dashboards/                    # Day 5: Exported Tableau Dashboard PNGs
│   └── Bluestock_Analytical_dashboard.pdf # Day 5: Consolidated Dashboard PDF
├── scripts/
│   ├── compute_var_cvar.py            # Task 1: Historical VaR & CVaR computation (Day 6)
│   ├── compute_rolling_sharpe.py      # Task 2: Rolling 90-day Sharpe chart (Day 6)
│   ├── compute_cohort_analysis.py     # Task 3: Investor cohort analysis (Day 6)
│   ├── compute_sip_continuity.py      # Task 4: SIP continuity & at-risk flagging (Day 6)
│   ├── recommender.py                 # Task 5: Fund recommendation engine (Day 6)
│   ├── compute_sector_hhi.py          # Task 6: Sector HHI analysis & chart (Day 6)
│   ├── build_day4.py                  # Script to build Day 4 performance analytics
│   ├── build_eda.py                   # Script to programmatically build the EDA notebook
│   ├── load_to_sqlite.py              # ETL Script to recreate and populate the database
│   ├── live_nav_fetch.py              # Live NAV retrieval API client
│   └── generate_scheme_navs.py        # Utility to match schemes with NAV datasets
└── sql/
    ├── schema.sql                     # Database Schema (8 Tables, 3 Views, 18 Indexes)
    └── queries.sql                    # 10 BI and analytical SQL queries
```

---

## 📅 Roadmap & Progress

### ✅ Day 1: Ingestion & Live NAV Fetching
- Consolidated **20 raw NAV history CSV files** (55,397 records).
- Implemented and verified mappings between `fund_master` and NAV records using AMFI codes.
- Integrated with `mfapi.in` API to fetch real-time NAV prices dynamically.

### ✅ Day 2: Data Cleaning, Schema Design & SQLite Integration
- **Advanced Data Cleaning:** Standardized datetimes, forward-fill NAV gaps, compliance audit flags.
- **Database Architecture:** 8 tables, 3 BI views, 18 indexes — 97,782 total rows loaded with FK enforcement.
- **Analytical Queries:** 10 queries in `sql/queries.sql` covering AUM, SIP trends, alpha/beta, KYC risk.

### ✅ Day 3: Exploratory Data Analysis (EDA)
- Programmatically built and executed `03_eda_analysis.ipynb`.
- Generated 11 publication-quality charts; 10 key insights across NAV trends, AUM, investor demographics.

### ✅ Day 4: Fund Performance Analytics
- Computed CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown from NAV history.
- Built composite Fund Scorecard (0–100) and benchmark comparison charts.

### ✅ Day 5: Tableau Dashboard Development
- 4-page interactive BI dashboard in Tableau Public.
  - Page 1: Industry Overview | Page 2: Fund Performance
  - Page 3: Investor Analytics | Page 4: SIP & Market Trends
- Interactive drill-down linking Fund Scorecard → NAV vs Benchmark chart.

### ✅ Day 6: Advanced Analytics & Risk Metrics
**Objectives:** Implement risk metrics, investor behaviour analytics, fund recommendation logic, and sector concentration analysis.

#### Task 1 — Historical VaR (95%) & CVaR → `var_cvar_report.csv`
- Computed daily return distributions from 64K NAV rows across 40 funds.
- **VaR:** `np.percentile(returns, 5)` | **CVaR:** `returns[returns <= VaR].mean()`
- Key finding: **ABSL Small Cap** has highest VaR (−2.391% daily); Liquid funds near-zero (−0.02%).

#### Task 2 — Rolling 90-Day Sharpe Ratio → `rolling_sharpe_chart.png`
- `rolling(90).mean() / rolling(90).std() * sqrt(252)` for top 5 composite-score funds.
- All funds dipped into negative Sharpe mid-2022 (global rate-hike correction); recovered Q4 2022.

#### Task 3 — Investor Cohort Analysis → `cohort_analysis.csv`
- Cohort 2024: 4,624 investors, avg SIP ₹10,997, ₹21.5 Cr invested.
- Cohort 2025: 138 investors, avg SIP ₹13,505 (22.8% higher per SIP vs 2024 cohort).

#### Task 4 — SIP Continuity Analysis → `sip_continuity.csv`
- 1,362 qualifying investors (6+ SIPs); **1,332 (97.8%) flagged at-risk** (avg gap > 35 days).
- Mean gap: 64.9 days — prime cohort for SIP re-engagement campaigns.

#### Task 5 — Fund Recommendation Engine → `scripts/recommender.py`
- `FundRecommender` class: input = risk appetite (Low/Moderate/High), output = Top 3 by Sharpe.
- Run directly: `python scripts/recommender.py`

#### Task 6 — Sector Concentration (HHI) → `sector_hhi.csv` + `sector_hhi_chart.png`
- **HHI = Σ(sector_weight_i)²** across 32 equity funds.
- Most concentrated: Axis Bluechip Fund (HHI=0.297, 48.7% IT). Most diversified: UTI Mid Cap (HHI=0.124).

#### Task 7 — Advanced Analytics Notebook → `notebooks/Advanced_Analytics.ipynb`
- Master summary: 5 sections, data displays, charts, and 5 Key Insight markdown cells.
- Fully executable: `jupyter nbconvert --execute notebooks/Advanced_Analytics.ipynb`

---

## ⚙️ Setup and Execution

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Rerun the ETL Pipeline
```bash
python scripts/load_to_sqlite.py
```

### 3. Run Day 6 Analytics Scripts
```bash
python scripts/compute_var_cvar.py        # Task 1: VaR & CVaR
python scripts/compute_rolling_sharpe.py  # Task 2: Rolling Sharpe chart
python scripts/compute_cohort_analysis.py # Task 3: Investor cohorts
python scripts/compute_sip_continuity.py  # Task 4: SIP continuity
python scripts/recommender.py             # Task 5: Fund recommendations
python scripts/compute_sector_hhi.py      # Task 6: Sector HHI
```

### 4. Run the Advanced Analytics Notebook
```bash
jupyter notebook notebooks/Advanced_Analytics.ipynb
```

### 5. Run Analytical SQL Queries
```bash
sqlite3 data/db/bluestock_mf.db < sql/queries.sql
```
