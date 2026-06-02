-- Database Schema (D2 Deliverable)
-- SQLite schema for Bluestock Mutual Fund Analytics

CREATE TABLE IF NOT EXISTS funds (
    fund_id INTEGER PRIMARY KEY,
    fund_name TEXT NOT NULL,
    fund_category TEXT,
    aum REAL,
    expense_ratio REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nav_history (
    nav_id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL,
    nav_date DATE NOT NULL,
    nav_value REAL NOT NULL,
    FOREIGN KEY (fund_id) REFERENCES funds(fund_id),
    UNIQUE(fund_id, nav_date)
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL,
    metric_date DATE NOT NULL,
    sharpe_ratio REAL,
    cagr REAL,
    beta REAL,
    var_95 REAL,
    FOREIGN KEY (fund_id) REFERENCES funds(fund_id)
);

CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id INTEGER PRIMARY KEY,
    investor_id INTEGER,
    fund_id INTEGER NOT NULL,
    allocation_percentage REAL,
    investment_amount REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fund_id) REFERENCES funds(fund_id)
);

CREATE INDEX idx_fund_id ON nav_history(fund_id);
CREATE INDEX idx_nav_date ON nav_history(nav_date);
CREATE INDEX idx_portfolio_investor ON portfolio(investor_id);
