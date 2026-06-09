"""
Task 4 — SIP Continuity Analysis
Bluestock MF Capstone | Day 6

For investors with 6+ SIP transactions:
- Compute average gap (days) between consecutive SIP transactions
- Flag investors with avg gap > 35 days as 'at_risk'
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXN_PATH = os.path.join(BASE, "data", "processed", "clean_transactions.csv")
OUT_PATH = os.path.join(BASE, "data", "processed", "sip_continuity.csv")

# ── Load Data ──────────────────────────────────────────────────────────────────
print("Loading clean_transactions.csv ...")
txns = pd.read_csv(TXN_PATH, parse_dates=["transaction_date"])

# ── Step 1: Filter SIP Transactions Only ──────────────────────────────────────
sip_txns = txns[txns["transaction_type"] == "SIP"].copy()
# print(f"Total SIP transactions: {len(sip_txns):,}")

# ── Step 2: Sort by (investor_id, transaction_date) ───────────────────────────
sip_txns.sort_values(["investor_id", "transaction_date"], inplace=True)

# ── Step 3: Compute Per-Investor SIP Count and Average Gap ────────────────────
records = []

for investor_id, group in sip_txns.groupby("investor_id"):
    sip_count = len(group)

    if sip_count < 6:
        # Skip investors with fewer than 6 SIP transactions
        continue

    # Compute consecutive date differences
    date_diffs = group["transaction_date"].diff().dt.days
    # Drop the first NaN (no diff for the first SIP)
    gaps = date_diffs.dropna()

    avg_gap_days = gaps.mean()
    min_gap_days = gaps.min()
    max_gap_days = gaps.max()

    records.append({
        "investor_id":   investor_id,
        "sip_count":     sip_count,
        "avg_gap_days":  round(avg_gap_days, 2),
        "min_gap_days":  int(min_gap_days),
        "max_gap_days":  int(max_gap_days),
        "at_risk":       avg_gap_days > 35,
    })

result = pd.DataFrame(records)

# ── Assertions ─────────────────────────────────────────────────────────────────
print("\n--- Verification Assertions ---")
assert (result["sip_count"] >= 6).all(), "Some investors have fewer than 6 SIPs!"
assert result["at_risk"].dtype == bool, "at_risk must be boolean!"
assert result["avg_gap_days"].notna().all(), "Null avg_gap_days found!"
assert len(result) > 0, "No qualifying investors found!"

total   = len(result)
at_risk = result["at_risk"].sum()
safe    = total - at_risk
pct     = at_risk / total * 100

print(f"✅ All {total:,} investors have sip_count >= 6")
print(f"✅ at_risk is boolean")
print(f"✅ No null avg_gap_days")
print(f"\nAt-risk investors: {at_risk:,} ({pct:.1f}%)")
print(f"Healthy investors: {safe:,} ({100-pct:.1f}%)")

# ── Save ───────────────────────────────────────────────────────────────────────
result.to_csv(OUT_PATH, index=False)
print(f"\n✅ Saved → {OUT_PATH}")

# ── Summary Stats ──────────────────────────────────────────────────────────────
print("\n--- Distribution of avg_gap_days ---")
print(result["avg_gap_days"].describe().round(2))
print("\n--- Sample At-Risk Investors (avg gap > 35 days) ---")
print(result[result["at_risk"]].head(5).to_string(index=False))

print("\n✅ Task 4 complete — sip_continuity.csv saved.")
