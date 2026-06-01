-- Useful Queries (D2 Deliverable)
-- SQLite queries for Bluestock Mutual Fund Analytics

-- Get top performing funds by Sharpe ratio
SELECT 
    f.fund_name,
    f.fund_category,
    pm.sharpe_ratio,
    pm.cagr,
    pm.beta
FROM funds f
JOIN performance_metrics pm ON f.fund_id = pm.fund_id
ORDER BY pm.sharpe_ratio DESC
LIMIT 10;

-- Get latest NAV for all funds
SELECT 
    f.fund_name,
    nh.nav_value,
    nh.nav_date,
    LAG(nh.nav_value) OVER (PARTITION BY nh.fund_id ORDER BY nh.nav_date) as previous_nav
FROM funds f
JOIN nav_history nh ON f.fund_id = nh.fund_id
WHERE nh.nav_date = (SELECT MAX(nav_date) FROM nav_history)
ORDER BY f.fund_name;

-- Calculate returns over different periods
SELECT 
    f.fund_name,
    ROUND(((current_nav.nav_value - previous_nav.nav_value) / previous_nav.nav_value * 100), 2) as return_percentage
FROM funds f
JOIN nav_history current_nav ON f.fund_id = current_nav.fund_id
JOIN nav_history previous_nav ON f.fund_id = previous_nav.fund_id
WHERE current_nav.nav_date = DATE('now')
  AND previous_nav.nav_date = DATE('now', '-1 year')
ORDER BY return_percentage DESC;

-- Portfolio allocation summary
SELECT 
    f.fund_name,
    f.fund_category,
    SUM(p.allocation_percentage) as total_allocation,
    SUM(p.investment_amount) as total_invested
FROM portfolio p
JOIN funds f ON p.fund_id = f.fund_id
GROUP BY p.fund_id
ORDER BY total_invested DESC;
