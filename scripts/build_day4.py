"""
Module: build_day4.py

Part of the Bluestock Mutual Fund Analytics Capstone.
This script provides functionality for the data pipeline and analytics engine.
"""

import nbformat as nbf
import os
import subprocess

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

nb = nbf.v4.new_notebook()

# Ensure output directories exist
os.makedirs('data/processed', exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('notebooks', exist_ok=True)

# Task 1: Setup and Compute daily returns
setup_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
import warnings

warnings.filterwarnings('ignore')

# Ensure output directories exist
os.makedirs('../data/processed', exist_ok=True)
os.makedirs('../reports', exist_ok=True)

# Load data
nav_history = pd.read_csv('../data/raw/02_nav_history.csv')
fund_master = pd.read_csv('../data/raw/01_fund_master.csv')
scheme_perf = pd.read_csv('../data/raw/07_scheme_performance.csv')
benchmarks = pd.read_csv('../data/raw/10_benchmark_indices.csv')

# Format dates
nav_history['date'] = pd.to_datetime(nav_history['date'])
benchmarks['date'] = pd.to_datetime(benchmarks['date'])

# Sort by date
nav_history = nav_history.sort_values(by=['amfi_code', 'date'])

# Task 1: Compute daily returns for all funds
nav_history['daily_return'] = nav_history.groupby('amfi_code')['nav'].pct_change()

# Compute annualised return: (1 + daily_return).prod()^(252/n) - 1
returns_summary = []
for amfi_code, group in nav_history.groupby('amfi_code'):
    group = group.dropna(subset=['daily_return'])
    if len(group) == 0:
        continue
    total_return = (1 + group['daily_return']).prod()
    n_days = len(group)
    ann_return = total_return ** (252 / n_days) - 1 if n_days > 0 else np.nan
    returns_summary.append({
        'amfi_code': amfi_code,
        'annualised_return': ann_return
    })

returns_df = pd.DataFrame(returns_summary)
returns_df.to_csv('../data/processed/returns_computed.csv', index=False)
print("Task 1 completed. Saved to returns_computed.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 1: Compute Daily and Annualised Returns"))
nb.cells.append(nbf.v4.new_code_cell(setup_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/returns_computed.csv')
run_cmd('git commit -m "Task 1: Compute daily and annualised returns"')

# Task 2: CAGR for 1yr, 3yr, 5yr
task2_code = """
# Task 2: Calculate CAGR for 1yr, 3yr, 5yr periods
max_date = nav_history['date'].max()

def get_cagr(group, years):
    start_date = max_date - pd.DateOffset(years=years)
    mask = group['date'] >= start_date
    period_data = group[mask]
    if len(period_data) < 200 * years: # Require sufficient data points
        return np.nan
    
    nav_start = period_data.iloc[0]['nav']
    nav_end = period_data.iloc[-1]['nav']
    return (nav_end / nav_start) ** (1 / years) - 1

cagr_results = []
for amfi_code, group in nav_history.groupby('amfi_code'):
    group = group.sort_values('date')
    cagr_1yr = get_cagr(group, 1)
    cagr_3yr = get_cagr(group, 3)
    cagr_5yr = get_cagr(group, 5)
    cagr_results.append({
        'amfi_code': amfi_code,
        'cagr_1yr': cagr_1yr,
        'cagr_3yr': cagr_3yr,
        'cagr_5yr': cagr_5yr
    })

cagr_df = pd.DataFrame(cagr_results)
cagr_df.to_csv('../data/processed/cagr_report.csv', index=False)
print("Task 2 completed. Saved to cagr_report.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 2: Calculate CAGR for 1yr, 3yr, 5yr"))
nb.cells.append(nbf.v4.new_code_cell(task2_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/cagr_report.csv')
run_cmd('git commit -m "Task 2: Calculate CAGR for 1yr, 3yr, 5yr periods"')

# Task 3: Sharpe Ratio
task3_code = """
# Task 3: Compute Sharpe Ratio
# Sharpe = (Rp - Rf) / Std(Rp)
# Rf = 6.5% (0.065), annualise with sqrt(252)
rf_annual = 0.065
rf_daily = (1 + rf_annual) ** (1/252) - 1

sharpe_results = []
for amfi_code, group in nav_history.groupby('amfi_code'):
    group = group.dropna(subset=['daily_return'])
    if len(group) == 0:
        continue
    excess_returns = group['daily_return'] - rf_daily
    avg_excess_return = excess_returns.mean()
    std_excess_return = group['daily_return'].std()
    
    if std_excess_return > 0:
        daily_sharpe = avg_excess_return / std_excess_return
        ann_sharpe = daily_sharpe * np.sqrt(252)
    else:
        ann_sharpe = np.nan
        
    sharpe_results.append({
        'amfi_code': amfi_code,
        'sharpe_ratio': ann_sharpe
    })

sharpe_df = pd.DataFrame(sharpe_results)
sharpe_df.to_csv('../data/processed/sharpe_values.csv', index=False)
print("Task 3 completed. Saved to sharpe_values.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 3: Compute Sharpe Ratio"))
nb.cells.append(nbf.v4.new_code_cell(task3_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/sharpe_values.csv')
run_cmd('git commit -m "Task 3: Compute Sharpe Ratio"')

# Task 4: Sortino Ratio
task4_code = """
# Task 4: Compute Sortino Ratio
# Sortino = (Rp - Rf) / Downside_Std

sortino_results = []
for amfi_code, group in nav_history.groupby('amfi_code'):
    group = group.dropna(subset=['daily_return'])
    if len(group) == 0:
        continue
    excess_returns = group['daily_return'] - rf_daily
    avg_excess_return = excess_returns.mean()
    
    negative_returns = group.loc[group['daily_return'] < 0, 'daily_return']
    downside_std = np.sqrt(np.mean(negative_returns ** 2)) if len(negative_returns) > 0 else np.nan
    
    if downside_std > 0 and not np.isnan(downside_std):
        daily_sortino = avg_excess_return / downside_std
        ann_sortino = daily_sortino * np.sqrt(252)
    else:
        ann_sortino = np.nan
        
    sortino_results.append({
        'amfi_code': amfi_code,
        'sortino_ratio': ann_sortino
    })

sortino_df = pd.DataFrame(sortino_results)
sortino_df.to_csv('../data/processed/sortino_values.csv', index=False)
print("Task 4 completed. Saved to sortino_values.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 4: Compute Sortino Ratio"))
nb.cells.append(nbf.v4.new_code_cell(task4_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/sortino_values.csv')
run_cmd('git commit -m "Task 4: Compute Sortino Ratio"')

# Task 5: Alpha and Beta
task5_code = """
# Task 5: Compute Alpha & Beta vs benchmark
# Regress fund returns on Nifty 100 returns (OLS)
# Alpha = intercept * 252, Beta = slope

# Extract Nifty 100 daily returns
nifty100 = benchmarks[benchmarks['index_name'] == 'NIFTY100'].copy()
nifty100 = nifty100.sort_values('date')
nifty100['benchmark_return'] = nifty100['close_value'].pct_change()

alpha_beta_results = []
for amfi_code, group in nav_history.groupby('amfi_code'):
    group = group.dropna(subset=['daily_return'])
    if len(group) == 0:
        continue
    
    # Merge on date
    merged = pd.merge(group[['date', 'daily_return']], nifty100[['date', 'benchmark_return']], on='date', how='inner')
    merged = merged.dropna()
    
    if len(merged) > 10:
        slope, intercept, r_value, p_value, std_err = stats.linregress(merged['benchmark_return'], merged['daily_return'])
        ann_alpha = intercept * 252
        beta = slope
    else:
        ann_alpha = np.nan
        beta = np.nan
        
    alpha_beta_results.append({
        'amfi_code': amfi_code,
        'alpha': ann_alpha,
        'beta': beta
    })

alpha_beta_df = pd.DataFrame(alpha_beta_results)
alpha_beta_df.to_csv('../data/processed/alpha_beta.csv', index=False)
print("Task 5 completed. Saved to alpha_beta.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 5: Compute Alpha & Beta vs benchmark"))
nb.cells.append(nbf.v4.new_code_cell(task5_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/alpha_beta.csv')
run_cmd('git commit -m "Task 5: Compute Alpha and Beta"')

# Task 6: Maximum Drawdown
task6_code = """
# Task 6: Compute Maximum Drawdown
# max_dd = min(NAV / running_max - 1)
# Highlight worst drawdown period for each fund

max_dd_results = []
for amfi_code, group in nav_history.groupby('amfi_code'):
    group = group.sort_values('date').copy()
    group['running_max'] = group['nav'].cummax()
    group['drawdown'] = group['nav'] / group['running_max'] - 1
    
    max_dd = group['drawdown'].min()
    
    # Find the period
    if max_dd < 0:
        worst_dd_date = group.loc[group['drawdown'].idxmin(), 'date']
        peak_date = group.loc[(group['date'] <= worst_dd_date) & (group['drawdown'] == 0), 'date'].max()
    else:
        worst_dd_date = pd.NaT
        peak_date = pd.NaT
        
    max_dd_results.append({
        'amfi_code': amfi_code,
        'max_drawdown': max_dd,
        'peak_date': peak_date,
        'worst_dd_date': worst_dd_date
    })

max_dd_df = pd.DataFrame(max_dd_results)
max_dd_df.to_csv('../data/processed/max_drawdown.csv', index=False)
print("Task 6 completed. Saved to max_drawdown.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 6: Compute Maximum Drawdown"))
nb.cells.append(nbf.v4.new_code_cell(task6_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/max_drawdown.csv')
run_cmd('git commit -m "Task 6: Compute Maximum Drawdown"')

# Task 7: Fund Scorecard
task7_code = """
# Task 7: Build Fund Scorecard (composite score 0-100)
# Score = 30% * (3yr return rank) + 25% * (Sharpe rank) + 20% * (Alpha rank) + 15% * (Expense ratio rank, inverse) + 10% * (Max DD rank, inverse)

# Merge all metrics
scorecard_df = pd.merge(cagr_df[['amfi_code', 'cagr_3yr']], sharpe_df, on='amfi_code', how='left')
scorecard_df = pd.merge(scorecard_df, alpha_beta_df[['amfi_code', 'alpha']], on='amfi_code', how='left')
scorecard_df = pd.merge(scorecard_df, max_dd_df[['amfi_code', 'max_drawdown']], on='amfi_code', how='left')
scorecard_df = pd.merge(scorecard_df, scheme_perf[['amfi_code', 'expense_ratio_pct']], on='amfi_code', how='left')

# Drop NA for scoring
scorecard_df = scorecard_df.dropna()

# Percentile ranks (higher is better for returns, sharpe, alpha)
scorecard_df['rank_3yr'] = scorecard_df['cagr_3yr'].rank(pct=True) * 100
scorecard_df['rank_sharpe'] = scorecard_df['sharpe_ratio'].rank(pct=True) * 100
scorecard_df['rank_alpha'] = scorecard_df['alpha'].rank(pct=True) * 100

# Inverse ranks (lower is better for expense ratio, max DD)
# For max DD, negative values closer to 0 are better. 
scorecard_df['rank_max_dd'] = scorecard_df['max_drawdown'].rank(pct=True) * 100

# For expense ratio, lower is better. So ascending=False makes lowest expense ratio = 100th percentile.
scorecard_df['rank_expense'] = scorecard_df['expense_ratio_pct'].rank(pct=True, ascending=False) * 100

scorecard_df['composite_score'] = (
    0.30 * scorecard_df['rank_3yr'] +
    0.25 * scorecard_df['rank_sharpe'] +
    0.20 * scorecard_df['rank_alpha'] +
    0.15 * scorecard_df['rank_expense'] +
    0.10 * scorecard_df['rank_max_dd']
)

scorecard_df = scorecard_df.sort_values('composite_score', ascending=False)
scorecard_df.to_csv('../data/processed/fund_scorecard.csv', index=False)
print("Task 7 completed. Saved to fund_scorecard.csv")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 7: Build Fund Scorecard"))
nb.cells.append(nbf.v4.new_code_cell(task7_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb data/processed/fund_scorecard.csv')
run_cmd('git commit -m "Task 7: Build Fund Scorecard"')

# Task 8: Benchmark Comparison Chart
task8_code = """
# Task 8: Benchmark comparison chart
# Plot top 5 funds vs Nifty 50 and Nifty 100 over 3 years. Compute tracking error.

top_5_amfi = scorecard_df.head(5)['amfi_code'].tolist()

# 3 years ago from max date
max_date = nav_history['date'].max()
start_date = max_date - pd.DateOffset(years=3)

plt.figure(figsize=(14, 8))

# Plot Nifty 50
nifty50 = benchmarks[(benchmarks['index_name'] == 'NIFTY50') & (benchmarks['date'] >= start_date)].sort_values('date')
if not nifty50.empty:
    n50_base = nifty50.iloc[0]['close_value']
    plt.plot(nifty50['date'], (nifty50['close_value'] / n50_base) * 100, label='NIFTY 50', linewidth=2, linestyle='--')

# Plot Nifty 100
nifty100 = benchmarks[(benchmarks['index_name'] == 'NIFTY100') & (benchmarks['date'] >= start_date)].sort_values('date')
if not nifty100.empty:
    n100_base = nifty100.iloc[0]['close_value']
    nifty100['benchmark_return'] = nifty100['close_value'].pct_change()
    plt.plot(nifty100['date'], (nifty100['close_value'] / n100_base) * 100, label='NIFTY 100', linewidth=2, linestyle='--')

tracking_errors = []

for amfi in top_5_amfi:
    fund_data = nav_history[(nav_history['amfi_code'] == amfi) & (nav_history['date'] >= start_date)].sort_values('date')
    if not fund_data.empty:
        fund_base = fund_data.iloc[0]['nav']
        name = fund_master[fund_master['amfi_code'] == amfi]['scheme_name'].iloc[0] if len(fund_master[fund_master['amfi_code'] == amfi]) > 0 else str(amfi)
        plt.plot(fund_data['date'], (fund_data['nav'] / fund_base) * 100, label=name)
        
        # Calculate tracking error vs Nifty 100
        merged = pd.merge(fund_data[['date', 'daily_return']], nifty100[['date', 'benchmark_return']], on='date')
        if not merged.empty:
            diff = merged['daily_return'] - merged['benchmark_return']
            te = diff.std() * np.sqrt(252)
            tracking_errors.append({'scheme': name, 'tracking_error_ann': te})

plt.title('Top 5 Funds vs Benchmarks (Base 100) - Last 3 Years')
plt.xlabel('Date')
plt.ylabel('Normalized Value')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../reports/benchmark_chart.png')
print("Task 8 completed. Chart saved to benchmark_chart.png")

print("Tracking Errors vs NIFTY 100:")
for te in tracking_errors:
    print(f"{te['scheme']}: {te['tracking_error_ann']:.2%}")
"""
nb.cells.append(nbf.v4.new_markdown_cell("## Task 8: Benchmark comparison chart"))
nb.cells.append(nbf.v4.new_code_cell(task8_code))

with open('notebooks/Performance_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

run_cmd('jupyter nbconvert --to notebook --execute --inplace notebooks/Performance_Analytics.ipynb')
run_cmd('git add -f notebooks/Performance_Analytics.ipynb reports/benchmark_chart.png')
run_cmd('git commit -m "Task 8: Benchmark comparison chart"')

print("All tasks completed.")
