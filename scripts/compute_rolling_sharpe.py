"""
Task 2 — Rolling 90-Day Sharpe Ratio Chart
Bluestock MF Capstone | Day 6

Formula: rolling_sharpe = returns.rolling(90).mean() / returns.rolling(90).std() * sqrt(252)
Plots top 5 funds by composite score from fund_scorecard.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving files
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV_PATH      = os.path.join(BASE, "data", "processed", "clean_nav.csv")
SCORECARD_PATH= os.path.join(BASE, "data", "processed", "fund_scorecard.csv")
PERF_PATH     = os.path.join(BASE, "data", "processed", "clean_performance.csv")
OUT_IMG       = os.path.join(BASE, "notebooks", "reports", "rolling_sharpe_chart.png")

# ── Select Top 5 Funds by Composite Score ─────────────────────────────────────
scorecard = pd.read_csv(SCORECARD_PATH)
top5_codes = (
    scorecard.sort_values("composite_score", ascending=False)
    .head(5)["amfi_code"]
    .tolist()
)
print(f"Top 5 funds (by composite score): {top5_codes}")

# ── Load Performance for Short Names ──────────────────────────────────────────
perf = pd.read_csv(PERF_PATH)[["amfi_code", "scheme_name"]]

def short_name(full_name):
    """Extract fund house + short scheme name for legend."""
    name = full_name.split(" - ")[0]  # drop "Regular Plan - Growth" etc.
    # shorten long names
    replacements = {
        "Mirae Asset Large Cap Fund": "Mirae Asset Large Cap",
        "ICICI Pru Midcap Fund": "ICICI Pru Midcap",
        "Kotak Flexicap Fund": "Kotak Flexicap",
        "HDFC Mid-Cap Opportunities Fund": "HDFC Mid-Cap",
        "ICICI Pru Bluechip Fund": "ICICI Pru Bluechip",
    }
    return replacements.get(name, name[:35])

# ── Load NAV Data ──────────────────────────────────────────────────────────────
print("Loading clean_nav.csv ...")
nav = pd.read_csv(NAV_PATH, parse_dates=["date"])
nav.sort_values(["amfi_code", "date"], inplace=True)

# Filter to top 5 funds only
nav_top5 = nav[nav["amfi_code"].isin(top5_codes)].copy()

# ── Compute Daily Returns ──────────────────────────────────────────────────────
nav_top5["daily_return"] = nav_top5.groupby("amfi_code")["nav"].pct_change()

# ── Compute Rolling 90-Day Sharpe per Fund ─────────────────────────────────────
print("Computing rolling 90-day Sharpe ratios ...")
rolling_results = {}

for code in top5_codes:
    fund_data = nav_top5[nav_top5["amfi_code"] == code].set_index("date")["daily_return"].dropna()

    roll_mean = fund_data.rolling(window=90).mean()
    roll_std  = fund_data.rolling(window=90).std()

    # Avoid division by zero for flat funds (e.g. liquid)
    rolling_sharpe = np.where(
        roll_std > 1e-8,
        roll_mean / roll_std * np.sqrt(252),
        np.nan
    )
    rolling_results[code] = pd.Series(rolling_sharpe, index=fund_data.index)

# ── Build Name Map ─────────────────────────────────────────────────────────────
name_map = {}
for code in top5_codes:
    row = perf[perf["amfi_code"] == code]
    if not row.empty:
        name_map[code] = short_name(row.iloc[0]["scheme_name"])
    else:
        name_map[code] = str(code)

# ── Plot ───────────────────────────────────────────────────────────────────────
print("Generating chart ...")
fig, ax = plt.subplots(figsize=(14, 7))

# Colour palette
colors = ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0", "#F44336"]

for i, code in enumerate(top5_codes):
    series = rolling_results[code].dropna()
    ax.plot(series.index, series.values,
            label=name_map[code],
            color=colors[i],
            linewidth=1.8,
            alpha=0.9)

# Zero reference line
ax.axhline(y=0, color="crimson", linestyle="--", linewidth=1.2,
           label="Break-even (Sharpe = 0)")

# Formatting
ax.set_title("Rolling 90-Day Sharpe Ratio — Top 5 Funds (2022–2025)",
             fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Rolling 90-Day Sharpe Ratio (Annualised)", fontsize=12)
ax.legend(loc="upper left", fontsize=9, framealpha=0.85)
ax.grid(True, alpha=0.3, linestyle="--")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

# Save
os.makedirs(os.path.dirname(OUT_IMG), exist_ok=True)
plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight")
plt.close()

# ── Verification ───────────────────────────────────────────────────────────────
file_size = os.path.getsize(OUT_IMG)
assert file_size > 10_000, f"Chart file too small ({file_size} bytes) — likely blank!"
print(f"\n✅ Saved → {OUT_IMG}  ({file_size / 1024:.1f} KB)")
print("✅ Task 2 complete — rolling_sharpe_chart.png saved.")
