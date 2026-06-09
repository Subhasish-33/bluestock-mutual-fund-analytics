# Bluestock Mutual Fund Analytics Capstone - Final Report

## 1. Executive Summary

The Bluestock Mutual Fund Analytics Capstone project was designed to construct an end-to-end data pipeline, analytics engine, and interactive dashboard for evaluating mutual fund performance. As the mutual fund industry grows in complexity, robust, data-driven tools are required to accurately track daily Net Asset Values (NAV), calculate vital performance and risk metrics, and visualize insights for stakeholders.

Throughout this 7-day project, we successfully:
- **Engineered an automated ETL pipeline** fetching live NAV data from the AMFI (Association of Mutual Funds in India) API.
- **Constructed a localized SQLite data warehouse** serving as the single source of truth for both historical and daily transactional data.
- **Performed comprehensive Exploratory Data Analysis (EDA)** to clean, validate, and understand the raw data, resolving data quality issues such as missing values and anomalies.
- **Computed standard and advanced performance/risk metrics** including CAGR, Volatility, Sharpe Ratio, Maximum Drawdown, Value at Risk (VaR), and Conditional Value at Risk (CVaR).
- **Developed advanced analytics modules** such as Sector Concentration (HHI), SIP Continuity Analysis, and Cohort tracking.
- **Built an interactive multi-page Streamlit Dashboard** to visualize all findings dynamically, allowing stakeholders to filter funds by category, risk level, and time horizon.
- **Implemented Bonus Objectives** including a Scheduled ETL Wrapper, a Monte Carlo GBM simulator for 5-year NAV projections, Portfolio Optimisation (Markowitz Efficient Frontier), and an Automated Email Report generator.

This report details the methodologies, findings, and technical architecture employed to achieve these results.

---

## 2. Data Sources and Architecture

### 2.1 Data Sources
The primary data sources for this project include:
1. **AMFI API (`https://www.amfiindia.com/spages/NAVAll.txt`)**: Provided the daily live NAVs for all open-ended mutual fund schemes in India.
2. **Static Historical CSVs**: Provided baseline historical NAV data, scheme metadata (category, sub-category, fund house), and simulated transaction data.
   - `nav_history.csv`: Historical NAVs over a 5-year period.
   - `mutual_fund_metadata.csv`: Details on scheme names, categories, risk profiles, and AUM.
   - `transactions.csv`: Synthesized data tracking daily investor inflows and outflows.

### 2.2 System Architecture
The system follows a modern data engineering pipeline architecture:
- **Extraction**: Python `requests` library pulls daily data from AMFI and reads historical CSVs using `pandas`.
- **Transformation**: Data cleaning, schema enforcement, date parsing, and missing value imputation were handled via `pandas`. Advanced metric computations utilized `numpy` and `scipy`.
- **Loading**: A localized relational `SQLite` database (`data/db/bluestock_mf.db`) was implemented to store cleaned dimensions and fact tables (`nav_history`, `metadata`, `transactions`, `performance_metrics`, etc.).
- **Presentation Layer**: A `Streamlit` web application serves as the interactive frontend, querying the SQLite database and rendering interactive visualizations via `plotly`.
- **Automation**: The `schedule` library runs a background worker script fetching daily NAVs at 8:00 PM on weekdays.

---

## 3. ETL Process Details

### 3.1 Data Ingestion & Cleaning
The ingestion phase merged historical batch data with daily streaming AMFI data. Key transformations included:
- **Standardization of Dates**: Converted all varied string formats to standard `datetime` objects (`YYYY-MM-DD`).
- **Data Type Casting**: Ensured all NAVs and AUMs were cast to `float64`, and scheme codes were treated as string identifiers.
- **Anomaly Detection**: Addressed outliers (e.g., negative NAVs) through localized forward-filling (`ffill`) to prevent skewed returns in risk modeling.
- **Schema Validation**: Validated that all required columns existed before insertion into the database to ensure referential integrity between `amfi_code` foreign keys.

### 3.2 Loading to SQLite
Using `sqlalchemy` and `sqlite3`, the clean datasets were loaded into a structured relational format. By using explicit schema definitions and enforcing primary/foreign key constraints, we ensure the integrity of the data warehouse.

---

## 4. EDA Findings

Exploratory Data Analysis revealed several crucial trends in the mutual fund landscape:

1. **AUM Distribution**: A significant skew in Assets Under Management exists, where the top 10% of funds control over 60% of total industry AUM. Large Cap and Flexi Cap equity funds dominate the upper quartile.
2. **Volatility Clusters**: Small Cap and Sectoral funds exhibited standard deviations significantly higher than Large Cap funds, confirming higher risk profiles.
3. **Missing Data Patterns**: We observed occasional missing NAVs during market holidays and weekends, which justified our decision to filter analytics based strictly on **trading days (approx. 252 days/year)**.
4. **Transaction Flows**: Seasonal trends were identified in transaction inflows, with peaks typically occurring at the beginning of the month (aligning with SIP deductions).

---

## 5. Performance and Risk Analysis

To robustly evaluate the funds, several statistical metrics were calculated.

### 5.1 Standard Metrics
- **CAGR (Compound Annual Growth Rate)**: Calculated using the formula `(NAV_end / NAV_start) ^ (252 / N_days) - 1`. This accurately reflects trading-day annualized growth.
- **Annualized Volatility**: Derived by taking the standard deviation of daily returns and multiplying by `sqrt(252)`.
- **Sharpe Ratio**: Evaluated the risk-adjusted return, assuming a risk-free rate of 6% (typical Indian market benchmark).
- **Sortino Ratio**: Modified the Sharpe formula to only penalize downside volatility, giving a clearer picture for conservative investors.

### 5.2 Advanced Metrics (Day 5 & 6)
- **Maximum Drawdown**: Quantified the maximum observed loss from a peak to a trough before a new peak is attained. Crucial for assessing worst-case capital loss scenarios.
- **Value at Risk (VaR) & Conditional VaR (CVaR)**: Utilizing a 95% confidence interval, we modeled the expected downside risk. CVaR (Expected Shortfall) proved particularly valuable in highlighting the fat-tail risks present in certain aggressive Small Cap funds.
- **Sector Concentration (HHI)**: The Herfindahl-Hirschman Index was calculated. High HHI values in thematic funds accurately predicted higher volatility, proving the risk of under-diversification.
- **SIP Continuity**: Analyzed user cohorts to track SIP dropout rates, identifying a noticeable drop-off after 12 months.

---

## 6. Dashboard & Visualizations

*(Please insert screenshots of the Streamlit App here before converting to PDF)*

### 6.1 Dashboard Overview
[INSERT SCREENSHOT 1: Overall Dashboard View]

The interactive dashboard (`app.py`) empowers users to:
- Filter by Category, Sub-Category, Risk Profile, and Rating.
- View real-time NAV charts over customized date ranges.
- Compare multiple funds side-by-side.

### 6.2 Performance Deep Dive
[INSERT SCREENSHOT 2: Performance Comparison Chart]

The "Performance" tab visualizes rolling Sharpe ratios and CAGR vs Volatility scatter plots, immediately highlighting the Efficient Frontier among the filtered funds.

---

## 7. Recommendations

Based on our analytics pipeline, the following recommendations are made for the business:

1. **Automated Alerts for Breached VaR limits**: We recommend setting up automated alerts within the ETL pipeline that trigger if a fund's daily VaR exceeds a predefined threshold.
2. **Dynamic SIP Interventions**: Given the dropout rate observed in the SIP continuity analysis, automated nudges/emails should be triggered at month 11 to encourage users to maintain their SIPs.
3. **Diversification Engine**: Funds with exceptionally high HHI scores should trigger a recommendation to the investor to balance their portfolio with broad-market index funds.

---

## 8. Limitations and Future Work

### Limitations
- **Risk-Free Rate Assumption**: The 6% risk-free rate is static. In a volatile macro environment, tying this to live 10-year G-Sec yields would improve accuracy.
- **Database Scalability**: While SQLite is highly portable and excellent for this scope, a production environment tracking thousands of schemes over decades would require migrating to PostgreSQL or a cloud data warehouse (e.g., Snowflake, BigQuery).

### Future Enhancements
- **Live Order Execution**: Integration with broker APIs (like Zerodha Kite or Upstox) to execute buy/sell orders directly from the dashboard.
- **Machine Learning Integration**: Advancing the Monte Carlo simulator into an LSTM or Prophet-based time-series forecasting model for NAV predictions.

---
**End of Report**
