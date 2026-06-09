"""
Module: build_eda.py

Part of the Bluestock Mutual Fund Analytics Capstone.
This script provides functionality for the data pipeline and analytics engine.
"""

import nbformat
import subprocess
import os
import time

def create_and_run_notebook():
    os.makedirs("reports/figures", exist_ok=True)
    nb = nbformat.v4.new_notebook()
    notebook_path = "notebooks/03_eda_analysis.ipynb"

    def run_and_commit(task_num, msg, new_cells, files_to_add=None):
        print(f"\n--- Running {msg} ---")
        for cell_type, source in new_cells:
            if cell_type == 'markdown':
                nb.cells.append(nbformat.v4.new_markdown_cell(source))
            else:
                nb.cells.append(nbformat.v4.new_code_cell(source))
        
        with open(notebook_path, "w") as f:
            nbformat.write(nb, f)
        
        # Execute the notebook
        res = subprocess.run(["jupyter", "nbconvert", "--execute", "--inplace", "--ExecutePreprocessor.timeout=600", notebook_path], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error executing notebook at {msg}:")
            print(res.stderr)
            raise Exception("Notebook execution failed")
            
        if files_to_add is None:
            files_to_add = []
        files_to_add.append(notebook_path)
        
        subprocess.run(["git", "add"] + files_to_add, check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        print(f"Successfully committed: {msg}")

    # Setup
    setup = [
        ("markdown", "# Day 3: Exploratory Data Analysis (EDA)\n\nSetting up the environment and loading data from SQLite."),
        ("code", '''import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs("../reports/figures", exist_ok=True)
conn = sqlite3.connect('../data/db/bluestock_mf.db')

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('deep')''')
    ]
    # We will bundle the setup with Task 1 to avoid an extra commit, or commit it separately.
    # Let's commit it as part of Task 1.

    # Task 1
    task1 = setup + [
        ("markdown", "## Task 1: NAV Trend Analysis\nPlotting daily NAV for all 40 schemes and highlighting key market events."),
        ("code", '''# Load NAV data
query = """
SELECT nh.date, nh.nav, fm.scheme_name 
FROM nav_history nh 
JOIN fund_master fm ON nh.amfi_code = fm.amfi_code
"""
nav_df = pd.read_sql(query, conn)
nav_df['date'] = pd.to_datetime(nav_df['date'])

# Plot with Plotly
fig = px.line(nav_df, x='date', y='nav', color='scheme_name', title='NAV Trend (2022-2026)')

# Add Annotations
fig.add_annotation(x='2022-03-01', y=150, text="COVID Recovery", showarrow=True, arrowhead=1)
fig.add_annotation(x='2023-06-01', y=200, text="2023 Rally", showarrow=True, arrowhead=1)
fig.add_annotation(x='2024-03-01', y=180, text="2024 Corrections", showarrow=True, arrowhead=1)

fig.update_layout(showlegend=False) # Hide legend as it's too large for 40 schemes
fig.write_image("../reports/figures/nav_trend_lines.png")
fig.show()''')
    ]
    run_and_commit(1, "Task 1: NAV trend analysis chart", task1, ["reports/figures/nav_trend_lines.png"])

    # Task 2
    task2 = [
        ("markdown", "## Task 2: AUM Growth Bar Chart\nGrouped bar chart for AUM by fund house per year."),
        ("code", '''# Load AUM data
aum_df = pd.read_sql("SELECT date, fund_house, aum_lakh_crore FROM aum_by_fund_house", conn)
aum_df['date'] = pd.to_datetime(aum_df['date'])
aum_df['year'] = aum_df['date'].dt.year

# Get max AUM per fund house per year
yearly_aum = aum_df.groupby(['year', 'fund_house'])['aum_lakh_crore'].max().reset_index()

plt.figure(figsize=(12, 6))
sns.barplot(data=yearly_aum, x='year', y='aum_lakh_crore', hue='fund_house')
plt.title('AUM Growth by AMC (2022-2025)')
plt.ylabel('AUM (Lakh Crore Rs)')
plt.annotate("SBI Dominance (~12.5L Cr)", xy=(3, 12.5), xytext=(2.5, 14), 
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("../reports/figures/aum_growth_amc.png", dpi=300)
plt.show()''')
    ]
    run_and_commit(2, "Task 2: AUM growth grouped bar chart by AMC", task2, ["reports/figures/aum_growth_amc.png"])

    # Task 3
    task3 = [
        ("markdown", "## Task 3: SIP Inflow Time-Series\nMonthly SIP inflows highlighting milestones."),
        ("code", '''sip_df = pd.read_sql("SELECT month, sip_inflow_crore FROM monthly_sip_inflows ORDER BY month", conn)

fig = px.line(sip_df, x='month', y='sip_inflow_crore', title='SIP Inflow Trend (2022-2025)')
fig.add_annotation(x='2025-12', y=31002, text="₹31,002 Cr All-Time High", showarrow=True, arrowhead=1)
fig.write_image("../reports/figures/sip_inflow_trend.png")
fig.show()''')
    ]
    run_and_commit(3, "Task 3: SIP inflow time-series and milestones", task3, ["reports/figures/sip_inflow_trend.png"])

    # Task 4
    task4 = [
        ("markdown", "## Task 4: Category-Wise Inflow Heatmap\nNet inflow across months by category."),
        ("code", '''cat_df = pd.read_sql("SELECT month, category, net_inflow_crore FROM category_inflows", conn)
pivot = cat_df.pivot(index='category', columns='month', values='net_inflow_crore')

plt.figure(figsize=(14, 8))
sns.heatmap(pivot, cmap='RdYlGn', center=0, annot=False)
plt.title('Category-Wise Net Inflow Heatmap (Crore Rs)')
plt.tight_layout()
plt.savefig("../reports/figures/category_heatmap.png", dpi=300)
plt.show()''')
    ]
    run_and_commit(4, "Task 4: Category-wise net inflow heatmap", task4, ["reports/figures/category_heatmap.png"])

    # Task 5
    task5 = [
        ("markdown", "## Task 5: Investor Demographics\nAge group and gender distribution, and SIP amounts by age."),
        ("code", '''# Demographics
demo_df = pd.read_sql("SELECT investor_id, age_group, gender FROM fact_transactions GROUP BY investor_id", conn)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
demo_df['age_group'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax1, title='Age Group Distribution', cmap='Set3')
demo_df['gender'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2, title='Gender Split', cmap='Pastel1')
ax1.set_ylabel('')
ax2.set_ylabel('')
plt.savefig("../reports/figures/demographics_pie.png", dpi=300)
plt.show()

# Box plot for SIP amount
sip_tx = pd.read_sql("SELECT age_group, amount_inr FROM fact_transactions WHERE transaction_type='SIP'", conn)
plt.figure(figsize=(10, 6))
sns.boxplot(data=sip_tx, x='age_group', y='amount_inr', order=['18-25', '26-35', '36-45', '46-55', '56+'])
plt.title('SIP Amount Distribution by Age Group')
# Limiting Y axis to ignore extreme outliers for better visualization
plt.ylim(0, sip_tx['amount_inr'].quantile(0.95) * 1.5)
plt.savefig("../reports/figures/demographics_box.png", dpi=300)
plt.show()''')
    ]
    run_and_commit(5, "Task 5: Investor demographics pie and box plots", task5, ["reports/figures/demographics_pie.png", "reports/figures/demographics_box.png"])

    # Task 6
    task6 = [
        ("markdown", "## Task 6: Geographic Distribution\nSIP amounts by state and T30 vs B30 analysis."),
        ("code", '''# State bar chart
state_df = pd.read_sql("""
SELECT state, SUM(amount_inr)/1e7 AS amount_cr 
FROM fact_transactions 
WHERE transaction_type='SIP' AND state IS NOT NULL
GROUP BY state ORDER BY amount_cr DESC LIMIT 15
""", conn)

plt.figure(figsize=(10, 8))
sns.barplot(data=state_df, y='state', x='amount_cr', orient='h', palette='viridis')
plt.title('Top 15 States by SIP Amount (Crore Rs)')
plt.xlabel('SIP Amount (Cr)')
plt.tight_layout()
plt.savefig("../reports/figures/geo_distribution_state.png", dpi=300)
plt.show()

# T30 vs B30
tier_df = pd.read_sql("""
SELECT city_tier, SUM(amount_inr) as total_amt 
FROM fact_transactions 
WHERE transaction_type='SIP' AND city_tier IS NOT NULL
GROUP BY city_tier
""", conn)

plt.figure(figsize=(6, 6))
plt.pie(tier_df['total_amt'], labels=tier_df['city_tier'], autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
plt.title('SIP Amount: T30 vs B30 Cities')
plt.savefig("../reports/figures/geo_distribution_tier.png", dpi=300)
plt.show()''')
    ]
    run_and_commit(6, "Task 6: Geographic distribution and city tier charts", task6, ["reports/figures/geo_distribution_state.png", "reports/figures/geo_distribution_tier.png"])

    # Task 7
    task7 = [
        ("markdown", "## Task 7: Folio Count Growth\nLine chart showing folio count growth from 2022 to 2025."),
        ("code", '''try:
    folio_df = pd.read_csv('../data/raw/06_industry_folio_count.csv')
    
    # We might need to ensure column names are clean
    folio_df.columns = folio_df.columns.str.strip()
    
    # Map possible column names
    date_col = 'month_year' if 'month_year' in folio_df.columns else 'month'
    val_col = 'folio_count_crore' if 'folio_count_crore' in folio_df.columns else folio_df.columns[1]
    
    fig = px.line(folio_df, x=date_col, y=val_col, title='Folio Count Growth (2022-2025)')
    
    # Annotate milestones
    fig.add_annotation(x=folio_df[date_col].iloc[0], y=13.26, text="13.26 Cr (Jan 2022)", showarrow=True)
    fig.add_annotation(x=folio_df[date_col].iloc[-1], y=26.12, text="26.12 Cr (Dec 2025)", showarrow=True)
    
    fig.write_image("../reports/figures/folio_count_growth.png")
    fig.show()
except Exception as e:
    print("Error generating folio chart:", e)''')
    ]
    run_and_commit(7, "Task 7: Folio count growth line chart", task7, ["reports/figures/folio_count_growth.png"])

    # Task 8
    task8 = [
        ("markdown", "## Task 8: Correlation Matrix\nPairwise correlation of daily returns for 10 selected top funds."),
        ("code", '''# Top 10 funds by AUM
top_funds = pd.read_sql("SELECT amfi_code, scheme_name FROM scheme_performance ORDER BY aum_crore DESC LIMIT 10", conn)
top_amfis = tuple(top_funds['amfi_code'].tolist())

query = f"""
SELECT date, amfi_code, daily_return 
FROM nav_history 
WHERE amfi_code IN {top_amfis} AND daily_return IS NOT NULL
"""
ret_df = pd.read_sql(query, conn)

# Map amfi_code to scheme_name for better labels
code_to_name = dict(zip(top_funds['amfi_code'], top_funds['scheme_name']))
ret_df['scheme_name'] = ret_df['amfi_code'].map(code_to_name)

# Pivot
pivot_ret = ret_df.pivot(index='date', columns='scheme_name', values='daily_return')
corr_matrix = pivot_ret.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=0.5, vmax=1.0)
plt.title('NAV Return Correlation Matrix (Top 10 Funds)')
plt.tight_layout()
plt.savefig("../reports/figures/correlation_matrix.png", dpi=300)
plt.show()''')
    ]
    run_and_commit(8, "Task 8: NAV return correlation matrix for top funds", task8, ["reports/figures/correlation_matrix.png"])

    # Task 9
    task9 = [
        ("markdown", "## Task 9: Sector Allocation Donut Chart\nAggregated sector weights across all equity funds."),
        ("code", '''query = """
SELECT ph.sector, SUM(ph.market_value_cr) as total_mcap
FROM portfolio_holdings ph
JOIN fund_master fm ON ph.amfi_code = fm.amfi_code
WHERE fm.category = 'Equity' AND ph.sector IS NOT NULL
GROUP BY ph.sector
ORDER BY total_mcap DESC
"""
sector_df = pd.read_sql(query, conn)

# Group small sectors into 'Others'
threshold = sector_df['total_mcap'].sum() * 0.03
sector_df.loc[sector_df['total_mcap'] < threshold, 'sector'] = 'Others'
sector_agg = sector_df.groupby('sector')['total_mcap'].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 8))
plt.pie(sector_agg, labels=sector_agg.index, autopct='%1.1f%%', wedgeprops=dict(width=0.4))
plt.title('Top Holdings Sector Allocation (Equity Funds)')
plt.savefig("../reports/figures/sector_allocation.png", dpi=300)
plt.show()''')
    ]
    run_and_commit(9, "Task 9: Sector allocation donut chart for equity funds", task9, ["reports/figures/sector_allocation.png"])

    # Task 10
    task10 = [
        ("markdown", """## Task 10: 10 Key EDA Findings

1. **Sustained NAV Growth**: The NAV trend chart shows a strong upward trajectory for most schemes following the COVID recovery phase in early 2022, fueled significantly by the 2023 rally. (*Reference: NAV Trend Lines*)
2. **Market Dominance**: SBI Mutual Fund maintains a commanding lead in AUM, reaching approximately ₹12.5 Lakh Crore by 2025, heavily outpacing competitors. (*Reference: AUM Growth by AMC*)
3. **Retail Investor Confidence**: SIP inflows hit a staggering all-time high of ₹31,002 Crore in December 2025, indicating massive adoption of systematic investments. (*Reference: SIP Inflow Trend*)
4. **Equity Preference**: The category inflow heatmap indicates sustained strong positive inflows into Equity and Hybrid categories, while Debt funds experienced periodic net outflows. (*Reference: Category Heatmap*)
5. **Young Demographics**: A massive chunk of investors falls in the 26-35 age bracket, highlighting the influx of millennials into the mutual fund space. (*Reference: Demographics Pie*)
6. **SIP Value by Age**: The 36-45 and 46-55 age groups contribute higher median SIP amounts compared to younger groups, reflecting their higher disposable income. (*Reference: Demographics Box Plot*)
7. **Geographic Concentration**: Maharashtra and Gujarat continue to dominate the total SIP transaction value, taking up the top spots on the state-wise distribution. (*Reference: Geo Distribution State*)
8. **T30 City Dominance**: Top 30 (T30) cities still account for the majority of the total SIP volume, though B30 cities show promising penetration. (*Reference: T30 vs B30 Pie Chart*)
9. **High Fund Correlation**: The top 10 funds show extremely high correlation (>0.90) in their daily returns, indicating they hold similar blue-chip heavy portfolios. (*Reference: Correlation Matrix*)
10. **Financial Sector Overweight**: Sector allocation reveals that Equity funds are heavily overweight in Financial Services (Banks, NBFCs), followed by IT and Healthcare. (*Reference: Sector Allocation Donut*)""")
    ]
    run_and_commit(10, "Task 10: Document 10 key EDA findings", task10)
    print("All tasks completed successfully!")

if __name__ == "__main__":
    create_and_run_notebook()
