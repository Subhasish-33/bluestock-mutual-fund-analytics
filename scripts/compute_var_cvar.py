"""
Task 1 — Historical VaR (95%) & CVaR
Bluestock MF Capstone | Day 6

VaR   = 5th percentile of daily return distribution  (negative value)
CVaR  = mean of all returns at or below VaR threshold (more negative than VaR)
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV_PATH = os.path.join(BASE, "data", "processed", "clean_nav.csv")
PERF_PATH= os.path.join(BASE, "data", "processed", "clean_performance.csv")
OUT_PATH = os.path.join(BASE, "data", "processed", "var_cvar_report.csv")

# ── Load Data ──────────────────────────────────────────────────────────────────
print("Loading clean_nav.csv ...")
nav = pd.read_csv(NAV_PATH, parse_dates=["date"])
nav.sort_values(["amfi_code", "date"], inplace=True)

print("Loading clean_performance.csv ...")
perf = pd.read_csv(PERF_PATH)[["amfi_code", "scheme_name", "category", "risk_grade"]]

# ── Compute Daily Returns ──────────────────────────────────────────────────────
print("Computing daily returns per fund ...")
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()

# ── VaR & CVaR per Fund ────────────────────────────────────────────────────────
records = []
for amfi_code, group in nav.dropna(subset=["daily_return"]).groupby("amfi_code"):
    returns = group["daily_return"].values

    # Historical VaR at 95% confidence = 5th percentile (negative number)
    var_95 = np.percentile(returns, 5)

    # CVaR = mean of returns <= VaR threshold (expected shortfall)
    cvar_95 = returns[returns <= var_95].mean()

    # Annualised VaR (for reference, not a deliverable column but useful)
    annualised_var = var_95 * np.sqrt(252)

    n_obs = len(returns)

    records.append({
        "amfi_code":         amfi_code,
        "var_95_pct":        round(var_95, 6),
        "cvar_95_pct":       round(cvar_95, 6),
        "annualised_var_pct":round(annualised_var, 6),
        "n_observations":    n_obs,
    })

results = pd.DataFrame(records)

# ── Merge Metadata ─────────────────────────────────────────────────────────────
results = results.merge(perf, on="amfi_code", how="left")

# ── Reorder Columns ────────────────────────────────────────────────────────────
results = results[[
    "amfi_code", "scheme_name", "category", "risk_grade",
    "var_95_pct", "cvar_95_pct", "annualised_var_pct", "n_observations"
]].sort_values("var_95_pct")  # most negative (riskiest) first

# ── Assertions ─────────────────────────────────────────────────────────────────
print("\n--- Verification Assertions ---")
assert len(results) == 40, f"Expected 40 funds, got {len(results)}"
assert (results["cvar_95_pct"] <= results["var_95_pct"]).all(), \
    "CVaR must be <= VaR (more negative) for all funds!"
assert results["var_95_pct"].lt(0).all(), \
    "VaR (5th pctl) must be negative for all funds!"
print("✅ All 40 funds present")
print("✅ CVaR <= VaR for all funds")
print("✅ VaR is negative for all funds")

# ── Save ───────────────────────────────────────────────────────────────────────
results.to_csv(OUT_PATH, index=False)
print(f"\n✅ Saved → {OUT_PATH}")

# ── Summary Stats ──────────────────────────────────────────────────────────────
print("\n--- Top 5 Most Risky Funds (by VaR) ---")
print(results[["scheme_name", "category", "risk_grade", "var_95_pct", "cvar_95_pct"]].head(5).to_string(index=False))
print("\n--- Top 5 Least Risky Funds (by VaR) ---")
print(results[["scheme_name", "category", "risk_grade", "var_95_pct", "cvar_95_pct"]].tail(5).to_string(index=False))

print("\n✅ Task 1 complete — var_cvar_report.csv saved.")
