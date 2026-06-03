# Data Dictionary — Bluestock Mutual Fund Analytics

**Capstone Project I | Day 2 Deliverable**  
**Database:** `data/db/bluestock_mf.db` (SQLite)  
**Last Updated:** 2026-06-03

---

## Overview

The database contains **8 tables** populated from **10 raw CSV sources** and **3 cleaned CSVs**, covering 97,782 total rows across fund metadata, daily NAV history, investor transactions, performance metrics, and portfolio holdings.

---

## Table 1: `fund_master`  *(alias view: `dim_fund`)*

**Source:** `data/raw/01_fund_master.csv`  
**Rows:** 40  
**Description:** Master dimension table for all 40 mutual fund schemes tracked in this project.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `amfi_code` | INTEGER | NO | PRIMARY KEY | Unique AMFI scheme code assigned by the Association of Mutual Funds in India |
| `fund_house` | TEXT | NO | NOT NULL | AMC (Asset Management Company) name e.g. SBI Mutual Fund, HDFC |
| `scheme_name` | TEXT | NO | NOT NULL | Full official scheme name including plan and option |
| `category` | TEXT | NO | NOT NULL | SEBI broad category: Equity, Debt, Hybrid |
| `sub_category` | TEXT | YES | — | SEBI sub-category: Large Cap, Mid Cap, Small Cap, Liquid, Gilt, etc. |
| `plan` | TEXT | YES | — | Plan type: Regular or Direct |
| `launch_date` | DATE | NO | NOT NULL | Date the scheme was launched (YYYY-MM-DD) |
| `benchmark` | TEXT | YES | — | Primary benchmark index e.g. Nifty 50, BSE Sensex |
| `expense_ratio_pct` | REAL | YES | ≥0 AND ≤3 | Annual expense ratio as a percentage of AUM |
| `exit_load_pct` | REAL | YES | ≥0 | Exit load percentage charged on redemption |
| `min_sip_amount` | INTEGER | YES | >0 | Minimum SIP instalment amount in INR |
| `min_lumpsum_amount` | INTEGER | YES | >0 | Minimum lumpsum investment amount in INR |
| `fund_manager` | TEXT | YES | — | Name(s) of fund manager(s) |
| `risk_category` | TEXT | YES | IN ('Low','Moderate','Moderately High','High','Very High') | SEBI risk classification for the scheme |
| `sebi_category_code` | TEXT | YES | — | SEBI internal category code |

---

## Table 2: `nav_history`  *(alias view: `fact_nav`)*

**Source:** `data/processed/clean_nav.csv` (cleaned from `data/raw/02_nav_history.csv`)  
**Rows:** 64,320  
**Description:** Daily NAV (Net Asset Value) for all 40 schemes. Calendar gaps (weekends/holidays) have been forward-filled. `daily_return` is computed during ETL.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `amfi_code` | INTEGER | NO | PK + FK → fund_master | AMFI scheme identifier |
| `date` | DATE | NO | PRIMARY KEY (amfi_code, date) | NAV date in YYYY-MM-DD format |
| `nav` | REAL | NO | >0 | Net Asset Value in INR as of that date |
| `daily_return` | REAL | YES | — | Daily percentage return = (nav_t / nav_{t-1}) - 1; NULL for the first row of each fund |

**Date Range:** 2022-01-03 → 2026-05-29  
**Funds:** 40 unique amfi_codes, 1,608 calendar-day rows each

---

## Table 3: `aum_by_fund_house`

**Source:** `data/raw/03_aum_by_fund_house.csv`  
**Rows:** 90  
**Description:** Quarterly AUM (Assets Under Management) aggregated at the fund house level.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `date` | DATE | NO | PRIMARY KEY (date, fund_house) | Quarter-end date |
| `fund_house` | TEXT | NO | PRIMARY KEY (date, fund_house) | AMC name |
| `aum_lakh_crore` | REAL | YES | ≥0 | Total AUM in lakh crore INR |
| `aum_crore` | REAL | YES | ≥0 | Total AUM in crore INR |
| `num_schemes` | INTEGER | YES | >0 | Number of schemes operated by this fund house |

---

## Table 4: `monthly_sip_inflows`

**Source:** `data/raw/04_monthly_sip_inflows.csv`  
**Rows:** 48  
**Description:** Industry-wide monthly SIP (Systematic Investment Plan) statistics published by AMFI.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `month` | TEXT | NO | PRIMARY KEY; format: YYYY-MM | Month of reporting |
| `sip_inflow_crore` | REAL | YES | ≥0 | Total SIP inflow for that month in crore INR |
| `active_sip_accounts_crore` | REAL | YES | ≥0 | Number of active SIP accounts (in crore) |
| `new_sip_accounts_lakh` | REAL | YES | ≥0 | New SIP accounts registered that month (in lakh) |
| `sip_aum_lakh_crore` | REAL | YES | ≥0 | Total SIP AUM as of month-end in lakh crore INR |
| `yoy_growth_pct` | REAL | YES | — | Year-over-year growth in SIP inflow; NULL for base-year months |

---

## Table 5: `category_inflows`

**Source:** `data/raw/05_category_inflows.csv`  
**Rows:** 144  
**Description:** Monthly net inflows (purchases minus redemptions) broken down by SEBI fund category.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `month` | TEXT | NO | PRIMARY KEY (month, category); format: YYYY-MM | Month of reporting |
| `category` | TEXT | NO | PRIMARY KEY (month, category) | Fund category e.g. Large Cap, Mid Cap, Liquid |
| `net_inflow_crore` | REAL | YES | — | Net inflow in crore INR; negative values indicate net outflows |

---

## Table 6: `scheme_performance`  *(alias view: `fact_performance`)*

**Source:** `data/processed/clean_performance.csv` (cleaned from `data/raw/07_scheme_performance.csv`)  
**Rows:** 40  
**Description:** Point-in-time performance snapshot for all 40 schemes. Includes return metrics, risk ratios, and audit flags added during cleaning.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `amfi_code` | INTEGER | NO | PRIMARY KEY + FK → fund_master | AMFI scheme code |
| `scheme_name` | TEXT | NO | NOT NULL | Scheme name |
| `fund_house` | TEXT | NO | NOT NULL | AMC name |
| `category` | TEXT | NO | NOT NULL | SEBI category |
| `plan` | TEXT | YES | — | Regular or Direct |
| `return_1yr_pct` | REAL | YES | — | 1-year trailing return (%) |
| `return_3yr_pct` | REAL | YES | — | 3-year CAGR (%) |
| `return_5yr_pct` | REAL | YES | — | 5-year CAGR (%) |
| `benchmark_3yr_pct` | REAL | YES | — | Benchmark 3-year CAGR (%) for alpha calculation |
| `alpha` | REAL | YES | — | Jensen's Alpha — excess return vs benchmark |
| `beta` | REAL | YES | — | Market beta; measures fund sensitivity to benchmark movements |
| `sharpe_ratio` | REAL | YES | — | Sharpe ratio = (return - risk_free) / std_dev; higher is better |
| `sortino_ratio` | REAL | YES | — | Sortino ratio; like Sharpe but penalises downside volatility only |
| `std_dev_ann_pct` | REAL | YES | ≥0 | Annualised standard deviation of returns (%) |
| `max_drawdown_pct` | REAL | YES | — | Maximum peak-to-trough drawdown (%); typically negative |
| `aum_crore` | REAL | YES | ≥0 | AUM in crore INR as of data date |
| `expense_ratio_pct` | REAL | YES | ≥0 AND ≤3 | Annual total expense ratio (%) |
| `morningstar_rating` | INTEGER | YES | 1–5 | Morningstar star rating |
| `risk_grade` | TEXT | YES | — | Qualitative risk label (e.g. Moderate, Very High) |
| `negative_sharpe_flag` | INTEGER | YES | 0 or 1 | **Audit flag**: 1 if sharpe_ratio < 0 (added during cleaning) |
| `expense_ratio_out_of_range_flag` | INTEGER | YES | 0 or 1 | **Audit flag**: 1 if expense_ratio outside 0.1%–2.5% SEBI limit |

---

## Table 7: `portfolio_holdings`

**Source:** `data/raw/09_portfolio_holdings.csv`  
**Rows:** 322  
**Description:** Top equity holdings for each scheme as of the most recent portfolio disclosure date.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `amfi_code` | INTEGER | NO | PK + FK → fund_master | AMFI scheme code |
| `stock_symbol` | TEXT | NO | PRIMARY KEY (amfi_code, stock_symbol) | NSE/BSE stock ticker symbol |
| `stock_name` | TEXT | NO | NOT NULL | Full company name |
| `sector` | TEXT | YES | — | SEBI sector classification |
| `weight_pct` | REAL | YES | 0–100 | Portfolio weight as a percentage of total AUM |
| `market_value_cr` | REAL | YES | ≥0 | Market value of holding in crore INR |
| `current_price_inr` | REAL | YES | >0 | Stock price in INR at portfolio_date |
| `portfolio_date` | DATE | NO | NOT NULL | Date of portfolio disclosure (YYYY-MM-DD) |

---

## Table 8: `fact_transactions`

**Source:** `data/processed/clean_transactions.csv` (cleaned from `data/raw/08_investor_transactions.csv`)  
**Rows:** 32,778  
**Description:** Investor-level transaction records. Each row is one purchase (SIP/Lumpsum) or Redemption event by one investor in one scheme.

| Column | Type | Nullable | Constraint | Description |
|--------|------|----------|------------|-------------|
| `transaction_id` | INTEGER | NO | PRIMARY KEY AUTOINCREMENT | Surrogate key assigned during ETL load |
| `investor_id` | TEXT | NO | NOT NULL | Anonymised investor identifier (e.g. INV003054) |
| `transaction_date` | DATE | NO | NOT NULL | Date the transaction was executed (YYYY-MM-DD) |
| `amfi_code` | INTEGER | NO | FK → fund_master | Scheme in which transaction was made |
| `transaction_type` | TEXT | NO | IN ('SIP','Lumpsum','Redemption') | Type of transaction |
| `amount_inr` | REAL | NO | >0 | Transaction amount in INR |
| `state` | TEXT | YES | — | Indian state of investor's registered address |
| `city` | TEXT | YES | — | City of investor's registered address |
| `city_tier` | TEXT | YES | IN ('T30','B30') | T30 = top 30 cities; B30 = beyond top 30 cities |
| `age_group` | TEXT | YES | — | Investor age band e.g. 18-25, 26-35, 36-45, 46-55, 56+ |
| `gender` | TEXT | YES | IN ('Male','Female','Other') | Investor gender |
| `annual_income_lakh` | REAL | YES | ≥0 | Annual income in lakh INR |
| `payment_mode` | TEXT | YES | — | Payment method: UPI, Mandate, Cheque, NEFT, etc. |
| `kyc_status` | TEXT | NO | IN ('Verified','Pending','Rejected') | KYC compliance status at time of transaction |

---

## Alias Views

| View Name | Maps To | Purpose |
|-----------|---------|---------|
| `dim_fund` | `fund_master` | Star-schema dimension alias for BI tooling |
| `fact_nav` | `nav_history` | Star-schema fact alias for NAV queries |
| `fact_performance` | `scheme_performance` | Star-schema fact alias for performance queries |

---

## Raw Sources Not Directly Loaded

The following raw CSVs are used for reference or future analysis:

| File | Description | Status |
|------|-------------|--------|
| `06_industry_folio_count.csv` | Industry-level investor folio count | Loaded |
| `10_benchmark_indices.csv` | Daily benchmark index values (Nifty 50, etc.) | Available for Day 3+ EDA |

---

## Data Lineage Summary

```
data/raw/01_fund_master.csv          → fund_master (40 rows)
data/raw/02_nav_history.csv          
  → [cleaning: 02_data_cleaning.ipynb]
  → data/processed/clean_nav.csv     → nav_history (64,320 rows + daily_return)

data/raw/08_investor_transactions.csv
  → [cleaning: 03_clean_transactions.ipynb]
  → data/processed/clean_transactions.csv → fact_transactions (32,778 rows)

data/raw/07_scheme_performance.csv
  → [cleaning: 04_clean_performance.ipynb]
  → data/processed/clean_performance.csv → scheme_performance (40 rows)

data/raw/03_aum_by_fund_house.csv    → aum_by_fund_house (90 rows)
data/raw/04_monthly_sip_inflows.csv  → monthly_sip_inflows (48 rows)
data/raw/05_category_inflows.csv     → category_inflows (144 rows)
data/raw/09_portfolio_holdings.csv   → portfolio_holdings (322 rows)
```
