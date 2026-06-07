"""
Task 3 — Investor Cohort Analysis
Bluestock MF Capstone | Day 6

Cohort = year of investor's FIRST ever transaction (any type).
Metrics per cohort:
  - investor_count, avg_sip_amount, total_invested_cr
  - Top 3 preferred funds (by SIP count) per cohort
"""

import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXN_PATH  = os.path.join(BASE, "data", "processed", "clean_transactions.csv")
PERF_PATH = os.path.join(BASE, "data", "processed", "clean_performance.csv")
OUT_PATH  = os.path.join(BASE, "data", "processed", "cohort_analysis.csv")

# ── Load Data ──────────────────────────────────────────────────────────────────
print("Loading clean_transactions.csv ...")
txns = pd.read_csv(TXN_PATH, parse_dates=["transaction_date"])

perf = pd.read_csv(PERF_PATH)[["amfi_code", "scheme_name"]]

# ── Step 1: Determine Cohort Year per Investor ─────────────────────────────────
# Cohort = year of investor's FIRST transaction (any type)
cohort_map = (
    txns.groupby("investor_id")["transaction_date"]
    .min()
    .dt.year
    .rename("cohort_year")
)
txns["cohort_year"] = txns["investor_id"].map(cohort_map)

print(f"Cohort distribution:\n{txns['cohort_year'].value_counts().sort_index()}\n")

# ── Step 2: SIP-only transactions ─────────────────────────────────────────────
sip_txns = txns[txns["transaction_type"] == "SIP"].copy()

# ── Step 3: Core Cohort Stats ──────────────────────────────────────────────────
cohort_stats = (
    sip_txns.groupby("cohort_year")
    .agg(
        investor_count=("investor_id", "nunique"),
        avg_sip_amount=("amount_inr", "mean"),
        total_invested_inr=("amount_inr", "sum"),
        sip_transaction_count=("amount_inr", "count"),
    )
    .reset_index()
)
cohort_stats["avg_sip_amount"] = cohort_stats["avg_sip_amount"].round(2)
cohort_stats["total_invested_cr"] = (cohort_stats["total_invested_inr"] / 1e7).round(4)
cohort_stats.drop(columns=["total_invested_inr"], inplace=True)

# ── Step 4: Top 3 Preferred Funds per Cohort (by SIP count) ───────────────────
fund_pref = (
    sip_txns.groupby(["cohort_year", "amfi_code"])
    .size()
    .reset_index(name="sip_count")
    .sort_values(["cohort_year", "sip_count"], ascending=[True, False])
)

# Get top 3 fund names per cohort
top_fund_map = {}
for year, group in fund_pref.groupby("cohort_year"):
    top3_codes = group.head(3)["amfi_code"].tolist()
    for rank, code in enumerate(top3_codes, 1):
        row = perf[perf["amfi_code"] == code]
        fname = row.iloc[0]["scheme_name"].split(" - ")[0] if not row.empty else str(code)
        top_fund_map.setdefault(year, {})[f"top_fund_{rank}"] = fname

top_funds_df = pd.DataFrame.from_dict(top_fund_map, orient="index").reset_index()
top_funds_df.rename(columns={"index": "cohort_year"}, inplace=True)

# ── Step 5: Merge and Finalise ─────────────────────────────────────────────────
cohort_analysis = cohort_stats.merge(top_funds_df, on="cohort_year", how="left")
cohort_analysis = cohort_analysis[[
    "cohort_year", "investor_count", "avg_sip_amount",
    "total_invested_cr", "sip_transaction_count",
    "top_fund_1", "top_fund_2", "top_fund_3"
]]

# ── Assertions ─────────────────────────────────────────────────────────────────
print("--- Verification Assertions ---")
assert cohort_analysis["cohort_year"].isin([2024, 2025]).all(), \
    f"Unexpected cohort years: {cohort_analysis['cohort_year'].unique()}"
assert cohort_analysis["investor_count"].gt(0).all(), "Empty cohort detected!"
assert cohort_analysis["avg_sip_amount"].gt(0).all(), "SIP amounts must be positive!"
print("✅ Cohort years are 2024 and 2025 only")
print("✅ All cohorts have investors")
print("✅ All SIP amounts are positive")

# ── Save ───────────────────────────────────────────────────────────────────────
cohort_analysis.to_csv(OUT_PATH, index=False)
print(f"\n✅ Saved → {OUT_PATH}")

# ── Display ────────────────────────────────────────────────────────────────────
print("\n--- Cohort Analysis Summary ---")
print(cohort_analysis.to_string(index=False))

print("\n✅ Task 3 complete — cohort_analysis.csv saved.")
