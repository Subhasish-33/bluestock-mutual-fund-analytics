"""
Task 6 — Sector Concentration Analysis (Herfindahl-Hirschman Index)
Bluestock MF Capstone | Day 6

HHI = sum(weight_i ^ 2)  where weight_i = sector_weight_pct / 100
Higher HHI = more concentrated portfolio (closer to 1.0)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOLDINGS_PATH= os.path.join(BASE, "data", "raw", "09_portfolio_holdings.csv")
PERF_PATH    = os.path.join(BASE, "data", "processed", "clean_performance.csv")
OUT_CSV      = os.path.join(BASE, "data", "processed", "sector_hhi.csv")
OUT_IMG      = os.path.join(BASE, "notebooks", "reports", "sector_hhi_chart.png")

# ── Load Data ──────────────────────────────────────────────────────────────────
print("Loading portfolio holdings ...")
holdings = pd.read_csv(HOLDINGS_PATH)

print("Loading clean_performance.csv ...")
perf = pd.read_csv(PERF_PATH)[["amfi_code", "scheme_name", "category", "risk_grade"]]

# ── Step 1: Exclude Non-Equity Funds ──────────────────────────────────────────
# Non-equity categories to exclude from HHI (Liquid, Gilt, Debt, Short Duration)
EXCLUDE_CATEGORIES = {"Liquid", "Gilt", "Short Duration", "Index/ETF", "Index"}

equity_perf = perf[~perf["category"].isin(EXCLUDE_CATEGORIES)].copy()
equity_codes = set(equity_perf["amfi_code"].unique())

holdings_equity = holdings[holdings["amfi_code"].isin(equity_codes)].copy()

print(f"Equity funds for HHI analysis: {len(equity_codes)}")
print(f"Total equity holdings rows: {len(holdings_equity)}")

# ── Step 2: Aggregate Sector Weights Per Fund ──────────────────────────────────
# Some stocks may appear in same sector for same fund — aggregate them
sector_weights = (
    holdings_equity
    .groupby(["amfi_code", "sector"])["weight_pct"]
    .sum()
    .reset_index()
)

# ── Step 3: Compute HHI ────────────────────────────────────────────────────────
# Convert % to decimal, then sum of squares
sector_weights["weight_decimal"] = sector_weights["weight_pct"] / 100.0
sector_weights["weight_sq"] = sector_weights["weight_decimal"] ** 2

hhi_df = (
    sector_weights
    .groupby("amfi_code")["weight_sq"]
    .sum()
    .reset_index()
    .rename(columns={"weight_sq": "hhi_score"})
)
hhi_df["hhi_score"] = hhi_df["hhi_score"].round(6)

# ── Step 4: Top Sector per Fund ────────────────────────────────────────────────
top_sector = (
    sector_weights
    .sort_values("weight_pct", ascending=False)
    .groupby("amfi_code")
    .first()
    .reset_index()[["amfi_code", "sector", "weight_pct"]]
    .rename(columns={"sector": "top_sector", "weight_pct": "top_sector_weight_pct"})
)

# ── Step 5: Merge Metadata ────────────────────────────────────────────────────
hhi_df = hhi_df.merge(equity_perf, on="amfi_code", how="left")
hhi_df = hhi_df.merge(top_sector, on="amfi_code", how="left")

# ── Final Output Schema ────────────────────────────────────────────────────────
hhi_df = hhi_df[[
    "amfi_code", "scheme_name", "category", "hhi_score",
    "top_sector", "top_sector_weight_pct"
]].sort_values("hhi_score", ascending=False).reset_index(drop=True)

# ── Assertions ─────────────────────────────────────────────────────────────────
print("\n--- Verification Assertions ---")
assert ((hhi_df["hhi_score"] > 0) & (hhi_df["hhi_score"] <= 1.0)).all(), \
    "HHI must be in (0, 1]!"
assert hhi_df["top_sector"].notna().all(), "Some funds missing top_sector!"
assert len(hhi_df) > 0, "No equity funds found!"
print(f"✅ HHI in (0, 1] for all {len(hhi_df)} equity funds")
print(f"✅ top_sector populated for all funds")

# ── Save CSV ───────────────────────────────────────────────────────────────────
hhi_df.to_csv(OUT_CSV, index=False)
print(f"\n✅ Saved CSV → {OUT_CSV}")

# ── Print Summary ──────────────────────────────────────────────────────────────
print("\n--- Top 5 Most Concentrated Funds ---")
print(hhi_df[["scheme_name", "hhi_score", "top_sector", "top_sector_weight_pct"]].head(5).to_string(index=False))
print("\n--- Top 5 Most Diversified Funds ---")
print(hhi_df[["scheme_name", "hhi_score", "top_sector", "top_sector_weight_pct"]].tail(5).to_string(index=False))

# ── Generate Chart ────────────────────────────────────────────────────────────
print("\nGenerating sector HHI chart ...")

# Sort ascending for chart (lowest HHI at top in horizontal bar)
chart_df = hhi_df.sort_values("hhi_score", ascending=True).copy()

# Short names for Y-axis
def short_name(full):
    name = full.split(" - ")[0]
    return name[:45]

chart_df["short_name"] = chart_df["scheme_name"].apply(short_name)

fig, ax = plt.subplots(figsize=(13, 10))

# Colour gradient: green (low HHI) → red (high HHI)
norm  = mcolors.Normalize(vmin=chart_df["hhi_score"].min(),
                           vmax=chart_df["hhi_score"].max())
cmap  = plt.cm.RdYlGn_r
colors= [cmap(norm(v)) for v in chart_df["hhi_score"]]

bars = ax.barh(chart_df["short_name"], chart_df["hhi_score"],
               color=colors, edgecolor="white", height=0.7)

# Value labels
for bar, val in zip(bars, chart_df["hhi_score"]):
    ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", ha="left", fontsize=8)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, fraction=0.02, pad=0.02)
cbar.set_label("HHI Score\n(higher = more concentrated)", fontsize=9)

ax.set_title("Sector Concentration (HHI) by Equity Fund",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("HHI Score  (0 = fully diversified, 1 = fully concentrated)",
              fontsize=10)
ax.set_ylabel("Fund", fontsize=10)
ax.grid(axis="x", alpha=0.3, linestyle="--")
ax.set_xlim(0, chart_df["hhi_score"].max() + 0.06)
plt.tight_layout()

os.makedirs(os.path.dirname(OUT_IMG), exist_ok=True)
plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight")
plt.close()

file_size = os.path.getsize(OUT_IMG)
assert file_size > 10_000, f"Chart file too small ({file_size} bytes)"
print(f"✅ Saved chart → {OUT_IMG}  ({file_size / 1024:.1f} KB)")
print("\n✅ Task 6 complete — sector_hhi.csv and sector_hhi_chart.png saved.")
