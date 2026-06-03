-- =============================================================================
-- Bluestock Mutual Fund Analytics — SQLite Database Schema
-- Day 2 | Part 2
-- =============================================================================
-- 7 normalized tables covering:
--   1. Fund Master (40 schemes)
--   2. NAV History (64K+ cleaned daily records)
--   3. AUM by Fund House (quarterly aggregates)
--   4. Monthly SIP Inflows (industry-level)
--   5. Category Inflows (monthly flows by category)
--   6. Scheme Performance (returns, ratios, risk metrics)
--   7. Portfolio Holdings (top holdings per scheme)
-- =============================================================================

-- Drop existing tables if re-running
DROP TABLE IF EXISTS portfolio_holdings;
DROP TABLE IF EXISTS scheme_performance;
DROP TABLE IF EXISTS category_inflows;
DROP TABLE IF EXISTS monthly_sip_inflows;
DROP TABLE IF EXISTS aum_by_fund_house;
DROP TABLE IF EXISTS nav_history;
DROP TABLE IF EXISTS fund_master;

-- =============================================================================
-- Table 1: fund_master
-- =============================================================================
-- Master table for all 40 mutual fund schemes
-- PK: amfi_code (unique scheme identifier used by AMFI)
-- =============================================================================

CREATE TABLE fund_master (
    amfi_code            INTEGER PRIMARY KEY,
    fund_house           TEXT NOT NULL,
    scheme_name          TEXT NOT NULL,
    category             TEXT NOT NULL,          -- Equity, Debt
    sub_category         TEXT,                   -- Large Cap, Mid Cap, etc.
    plan                 TEXT,                   -- Regular, Direct
    launch_date          DATE NOT NULL,
    benchmark            TEXT,
    expense_ratio_pct    REAL CHECK(expense_ratio_pct >= 0),
    exit_load_pct        REAL CHECK(exit_load_pct >= 0),
    min_sip_amount       INTEGER CHECK(min_sip_amount > 0),
    min_lumpsum_amount   INTEGER CHECK(min_lumpsum_amount > 0),
    fund_manager         TEXT,
    risk_category        TEXT,                   -- Low, Moderate, High, Very High
    sebi_category_code   TEXT
);

CREATE INDEX idx_fund_house ON fund_master(fund_house);
CREATE INDEX idx_category ON fund_master(category, sub_category);

-- =============================================================================
-- Table 2: nav_history
-- =============================================================================
-- Daily NAV (Net Asset Value) for all schemes
-- Cleaned dataset with forward-filled gaps (weekends/holidays)
-- PK: (amfi_code, date)
-- FK: amfi_code → fund_master
-- =============================================================================

CREATE TABLE nav_history (
    amfi_code   INTEGER NOT NULL,
    date        DATE NOT NULL,
    nav         REAL NOT NULL CHECK(nav > 0),
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_nav_date ON nav_history(date);
CREATE INDEX idx_nav_amfi_date ON nav_history(amfi_code, date);

-- =============================================================================
-- Table 3: aum_by_fund_house
-- =============================================================================
-- Quarterly AUM (Assets Under Management) aggregated by fund house
-- PK: (date, fund_house)
-- =============================================================================

CREATE TABLE aum_by_fund_house (
    date             DATE NOT NULL,
    fund_house       TEXT NOT NULL,
    aum_lakh_crore   REAL CHECK(aum_lakh_crore >= 0),     -- in lakh crore
    aum_crore        REAL CHECK(aum_crore >= 0),          -- in crore
    num_schemes      INTEGER CHECK(num_schemes > 0),
    PRIMARY KEY (date, fund_house)
);

CREATE INDEX idx_aum_date ON aum_by_fund_house(date);

-- =============================================================================
-- Table 4: monthly_sip_inflows
-- =============================================================================
-- Industry-wide SIP (Systematic Investment Plan) monthly inflow stats
-- PK: month (YYYY-MM format)
-- =============================================================================

CREATE TABLE monthly_sip_inflows (
    month                      TEXT PRIMARY KEY,  -- format: 'YYYY-MM'
    sip_inflow_crore           REAL CHECK(sip_inflow_crore >= 0),
    active_sip_accounts_crore  REAL CHECK(active_sip_accounts_crore >= 0),
    new_sip_accounts_lakh      REAL CHECK(new_sip_accounts_lakh >= 0),
    sip_aum_lakh_crore         REAL CHECK(sip_aum_lakh_crore >= 0),
    yoy_growth_pct             REAL   -- nullable for initial periods
);

CREATE INDEX idx_sip_month ON monthly_sip_inflows(month);

-- =============================================================================
-- Table 5: category_inflows
-- =============================================================================
-- Monthly net inflows by fund category (Large Cap, Mid Cap, Liquid, etc.)
-- PK: (month, category)
-- =============================================================================

CREATE TABLE category_inflows (
    month              TEXT NOT NULL,  -- format: 'YYYY-MM'
    category           TEXT NOT NULL,  -- Large Cap, Mid Cap, Small Cap, Liquid, etc.
    net_inflow_crore   REAL,           -- can be negative (outflows)
    PRIMARY KEY (month, category)
);

CREATE INDEX idx_catinf_month ON category_inflows(month);
CREATE INDEX idx_catinf_category ON category_inflows(category);

-- =============================================================================
-- Table 6: scheme_performance
-- =============================================================================
-- Performance metrics, returns, and risk indicators per scheme
-- PK: amfi_code (1:1 with fund_master; current snapshot as of data date)
-- FK: amfi_code → fund_master
-- =============================================================================

CREATE TABLE scheme_performance (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    category            TEXT NOT NULL,
    plan                TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL CHECK(std_dev_ann_pct >= 0),
    max_drawdown_pct    REAL,  -- typically negative
    aum_crore           REAL CHECK(aum_crore >= 0),
    expense_ratio_pct   REAL CHECK(expense_ratio_pct >= 0),
    morningstar_rating  INTEGER CHECK(morningstar_rating BETWEEN 1 AND 5),
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_perf_category ON scheme_performance(category);
CREATE INDEX idx_perf_rating ON scheme_performance(morningstar_rating);

-- =============================================================================
-- Table 7: portfolio_holdings
-- =============================================================================
-- Top equity holdings per scheme (as of portfolio_date)
-- Typically 8-12 stocks per scheme
-- PK: (amfi_code, stock_symbol)
-- FK: amfi_code → fund_master
-- =============================================================================

CREATE TABLE portfolio_holdings (
    amfi_code          INTEGER NOT NULL,
    stock_symbol       TEXT NOT NULL,
    stock_name         TEXT NOT NULL,
    sector             TEXT,
    weight_pct         REAL CHECK(weight_pct >= 0 AND weight_pct <= 100),
    market_value_cr    REAL CHECK(market_value_cr >= 0),  -- in crore
    current_price_inr  REAL CHECK(current_price_inr > 0),
    portfolio_date     DATE NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol),
    FOREIGN KEY (amfi_code) REFERENCES fund_master(amfi_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_holdings_symbol ON portfolio_holdings(stock_symbol);
CREATE INDEX idx_holdings_sector ON portfolio_holdings(sector);
CREATE INDEX idx_holdings_amfi ON portfolio_holdings(amfi_code);

-- =============================================================================
-- Schema Metadata
-- =============================================================================
-- Total tables: 7
-- Total indexes: 14 (including PKs)
-- Foreign Keys: 3 (all cascade on delete/update)
-- Check constraints: 22 (data integrity enforcement)
-- =============================================================================
