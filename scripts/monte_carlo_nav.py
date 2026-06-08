"""
Bonus Challenge 3: Monte Carlo NAV Projection
Bluestock MF Capstone

Uses Geometric Brownian Motion (GBM) to project 5-year NAV growth
for the top 5 funds (by composite score) with 1,000 simulations.

Formula (GBM):
    S(t) = S(t-1) * exp((mu - 0.5*sigma²)*dt + sigma*sqrt(dt)*Z)
    where Z ~ N(0,1), dt = 1 trading day

Outputs:
    - Median projection (50th percentile) per fund
    - Uncertainty band: 5th–95th percentile
    - Saved chart: notebooks/reports/monte_carlo_projection.png
"""

import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).resolve().parent.parent
NAV_PATH      = BASE / "data" / "processed" / "clean_nav.csv"
SCORECARD_PATH= BASE / "data" / "processed" / "fund_scorecard.csv"
PERF_PATH     = BASE / "data" / "processed" / "clean_performance.csv"
OUT_IMG       = BASE / "notebooks" / "reports" / "monte_carlo_projection.png"

# ── Simulation Parameters ─────────────────────────────────────────────────────
NUM_SIMULATIONS = 1000
NUM_DAYS        = 252 * 5   # 5 trading years


def run_monte_carlo():
    print("Loading data...")
    nav       = pd.read_csv(NAV_PATH, parse_dates=["date"])
    scorecard = pd.read_csv(SCORECARD_PATH)
    perf      = pd.read_csv(PERF_PATH)[["amfi_code", "scheme_name"]]

    # Top 5 funds by composite score
    top_funds = (
        scorecard.nlargest(5, "composite_score")["amfi_code"].tolist()
    )
    print(f"Top 5 funds selected: {top_funds}")

    # Build short name map
    name_map = {}
    for code in top_funds:
        row = perf[perf["amfi_code"] == code]
        if not row.empty:
            full = row.iloc[0]["scheme_name"]
            # Strip plan suffix for readability
            name_map[code] = full.split(" - ")[0][:35]
        else:
            name_map[code] = str(code)

    fig, ax = plt.subplots(figsize=(15, 8))
    colors = ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0", "#F44336"]

    for idx, amfi_code in enumerate(top_funds):
        fund_nav = (
            nav[nav["amfi_code"] == amfi_code]
            .sort_values("date")["nav"]
            .reset_index(drop=True)
        )
        daily_returns = fund_nav.pct_change().dropna()

        mu    = daily_returns.mean()
        sigma = daily_returns.std()
        S0    = fund_nav.iloc[-1]

        print(f"  [{amfi_code}] mu={mu:.6f}  sigma={sigma:.6f}  S0={S0:.4f}")

        # ── GBM simulation (vectorised) ───────────────────────────────────────
        dt = 1  # 1 trading day
        Z  = np.random.standard_normal((NUM_DAYS, NUM_SIMULATIONS))
        # Log-returns for each step
        log_returns = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z

        # Cumulative product from day 0
        paths = S0 * np.exp(np.cumsum(log_returns, axis=0))
        # Prepend the current NAV as day 0
        paths = np.vstack([np.full(NUM_SIMULATIONS, S0), paths])  # shape: (NUM_DAYS+1, N_SIM)

        # Percentile bands
        median_path = np.percentile(paths, 50, axis=1)
        lower_bound = np.percentile(paths,  5, axis=1)
        upper_bound = np.percentile(paths, 95, axis=1)

        x = range(len(median_path))
        color = colors[idx]
        ax.plot(x, median_path, color=color, linewidth=2,
                label=f"{name_map[amfi_code]} (median)")
        ax.fill_between(x, lower_bound, upper_bound,
                        color=color, alpha=0.12,
                        label=f"{name_map[amfi_code]} (5–95% band)")

    ax.set_title("5-Year Monte Carlo NAV Projection — Top 5 Funds (GBM, 1,000 simulations)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Trading Days into Future", fontsize=12)
    ax.set_ylabel("Projected NAV (₹)", fontsize=12)
    ax.legend(fontsize=8, loc="upper left", ncol=2, framealpha=0.85)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    plt.tight_layout()

    OUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight")
    plt.close()

    file_size = os.path.getsize(OUT_IMG)
    assert file_size > 10_000, f"Chart too small ({file_size} bytes) — something went wrong!"
    print(f"\n✅ Chart saved → {OUT_IMG}  ({file_size / 1024:.1f} KB)")
    print("✅ Monte Carlo simulation complete.")


if __name__ == "__main__":
    np.random.seed(42)   # reproducibility
    run_monte_carlo()
