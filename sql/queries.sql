-- =============================================================================
-- Bluestock Mutual Fund Analytics — 10 Analytical SQL Queries
-- Day 2 | Task 6
-- Database: bluestock_mf.db
-- =============================================================================

-- ─── Query 1: Top 5 Funds by AUM ───────────────────────────────────────────
-- Ranks all 40 schemes by their latest AUM (crore)

SELECT
    sp.amfi_code,
    sp.scheme_name,
    sp.fund_house,
    sp.category,
    ROUND(sp.aum_crore, 2)          AS aum_crore,
    sp.morningstar_rating,
    RANK() OVER (ORDER BY sp.aum_crore DESC) AS aum_rank
FROM scheme_performance sp
ORDER BY aum_crore DESC
LIMIT 5;

-- ─── Query 2: Average NAV Per Month (Industry-Wide) ────────────────────────
-- Average NAV across all funds for each calendar month

SELECT
    STRFTIME('%Y-%m', date)         AS month,
    ROUND(AVG(nav), 4)              AS avg_nav,
    COUNT(DISTINCT amfi_code)       AS num_funds,
    COUNT(*)                        AS total_rows
FROM nav_history
GROUP BY STRFTIME('%Y-%m', date)
ORDER BY month;

-- ─── Query 3: SIP Inflow Year-on-Year Growth ────────────────────────────────
-- Shows monthly SIP inflow and YoY growth percent

SELECT
    month,
    ROUND(sip_inflow_crore, 2)      AS sip_inflow_crore,
    ROUND(yoy_growth_pct, 2)        AS yoy_growth_pct
FROM monthly_sip_inflows
ORDER BY month;

-- ─── Query 4: Transactions Count by State ───────────────────────────────────
-- How many investor transactions originated from each state

SELECT
    state,
    COUNT(*)                        AS total_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2) AS total_amount_crore,
    ROUND(AVG(amount_inr), 2)       AS avg_amount_inr,
    COUNT(DISTINCT investor_id)     AS unique_investors
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;

-- ─── Query 5: Funds with Expense Ratio < 1% ─────────────────────────────────
-- Lists low-cost schemes — typically direct plans

SELECT
    sp.amfi_code,
    sp.scheme_name,
    sp.fund_house,
    sp.plan,
    sp.category,
    sp.expense_ratio_pct,
    sp.return_1yr_pct,
    sp.sharpe_ratio
FROM scheme_performance sp
WHERE sp.expense_ratio_pct < 1.0
ORDER BY sp.expense_ratio_pct ASC;

-- ─── Query 6: Top 5 Funds by 3-Year Risk-Adjusted Returns (Sharpe Ratio) ───
-- Identifies consistently well-performing funds after adjusting for volatility

SELECT
    sp.amfi_code,
    sp.scheme_name,
    sp.category,
    ROUND(sp.return_3yr_pct, 2)     AS return_3yr_pct,
    ROUND(sp.sharpe_ratio, 4)       AS sharpe_ratio,
    ROUND(sp.sortino_ratio, 4)      AS sortino_ratio,
    sp.morningstar_rating
FROM scheme_performance sp
ORDER BY sp.sharpe_ratio DESC
LIMIT 5;

-- ─── Query 7: Monthly SIP vs Lumpsum vs Redemption Transaction Volume ────────
-- Compares transaction volumes and amounts by type per month

SELECT
    STRFTIME('%Y-%m', transaction_date)  AS month,
    transaction_type,
    COUNT(*)                             AS num_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)     AS total_amount_crore,
    ROUND(AVG(amount_inr), 2)            AS avg_amount_inr
FROM fact_transactions
GROUP BY month, transaction_type
ORDER BY month, transaction_type;

-- ─── Query 8: Fund Performance vs Benchmark (Alpha Analysis) ────────────────
-- Shows which funds are generating alpha over their benchmarks

SELECT
    sp.amfi_code,
    sp.scheme_name,
    sp.fund_house,
    sp.category,
    ROUND(sp.return_3yr_pct, 2)       AS fund_return_3yr,
    ROUND(sp.benchmark_3yr_pct, 2)    AS benchmark_return_3yr,
    ROUND(sp.return_3yr_pct - sp.benchmark_3yr_pct, 2) AS excess_return,
    ROUND(sp.alpha, 4)                AS alpha,
    ROUND(sp.beta, 4)                 AS beta
FROM scheme_performance sp
ORDER BY excess_return DESC;

-- ─── Query 9: NAV Growth of Each Fund (1-Year Rolling Return) ───────────────
-- Computes actual NAV-based 1-year return from nav_history for each fund.
-- Uses a ±7-day tolerance window to handle weekends / market holidays.

SELECT
    n_now.amfi_code,
    fm.scheme_name,
    fm.category,
    ROUND(n_now.nav, 4)                                              AS current_nav,
    ROUND(n_1yr.nav, 4)                                              AS nav_1yr_ago,
    n_1yr.date                                                       AS date_1yr_ago,
    ROUND((n_now.nav - n_1yr.nav) / n_1yr.nav * 100.0, 2)           AS nav_1yr_return_pct
FROM nav_history n_now
JOIN (
    -- Pick the closest date to exactly 1 year ago (handles holidays/weekends)
    SELECT
        nh.amfi_code,
        nh.nav,
        nh.date
    FROM nav_history nh
    WHERE STRFTIME('%Y-%m-%d', nh.date) BETWEEN
              DATE((SELECT MAX(date) FROM nav_history), '-372 days') AND
              DATE((SELECT MAX(date) FROM nav_history), '-358 days')
    GROUP BY nh.amfi_code
    HAVING STRFTIME('%Y-%m-%d', nh.date) = MAX(STRFTIME('%Y-%m-%d', nh.date))
) n_1yr ON n_now.amfi_code = n_1yr.amfi_code
JOIN fund_master fm ON fm.amfi_code = n_now.amfi_code
WHERE STRFTIME('%Y-%m-%d', n_now.date) = (
    SELECT STRFTIME('%Y-%m-%d', MAX(date)) FROM nav_history
)
ORDER BY nav_1yr_return_pct DESC;

-- ─── Query 10: KYC-Pending Investor SIP Exposure ─────────────────────────────
-- Risk flag: how much SIP inflow is from investors with KYC still pending

SELECT
    t.kyc_status,
    t.transaction_type,
    COUNT(*)                             AS num_transactions,
    COUNT(DISTINCT t.investor_id)        AS unique_investors,
    ROUND(SUM(t.amount_inr) / 1e7, 2)   AS total_amount_crore,
    ROUND(AVG(t.amount_inr), 2)          AS avg_amount_inr
FROM fact_transactions t
WHERE t.transaction_type = 'SIP'
GROUP BY t.kyc_status, t.transaction_type
ORDER BY t.kyc_status;
