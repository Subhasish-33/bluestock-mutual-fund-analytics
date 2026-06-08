"""
Bonus Challenge 4: Markowitz Efficient Frontier
Bluestock MF Capstone

Computes the covariance matrix of daily returns for the top 5 funds
(by composite score), runs 10,000 random portfolio simulations, and
identifies the portfolios with:
  - Maximum Sharpe Ratio  (red star on chart)
  - Minimum Volatility    (green star on chart)

Outputs:
    - Console: allocation tables for the two optimal portfolios
    - Chart: notebooks/reports/efficient_frontier.png
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
OUT_IMG       = BASE / "notebooks" / "reports" / "efficient_frontier.png"

# ── Constants ─────────────────────────────────────────────────────────────────
RISK_FREE_ANNUAL = 0.065      # 6.5% per annum (India govt bond proxy)
NUM_PORTFOLIOS   = 10_000
NUM_ASSETS       = 5


def run_portfolio_optimisation():
    print("Loading data for portfolio optimisation...")
    nav       = pd.read_csv(NAV_PATH, parse_dates=["date"])
    scorecard = pd.read_csv(SCORECARD_PATH)
    perf      = pd.read_csv(PERF_PATH)[["amfi_code", "scheme_name"]]

    # Top 5 funds by composite score
    top_funds = (
        scorecard.nlargest(NUM_ASSETS, "composite_score")["amfi_code"].tolist()
    )
    print(f"Top 5 funds: {top_funds}")

    # Short names for labels
    name_map = {}
    for code in top_funds:
        row = perf[perf["amfi_code"] == code]
        name_map[code] = (
            row.iloc[0]["scheme_name"].split(" - ")[0][:30]
            if not row.empty else str(code)
        )

    # ── Build daily returns matrix ────────────────────────────────────────────
    nav_top   = nav[nav["amfi_code"].isin(top_funds)]
    pivot_nav = nav_top.pivot(index="date", columns="amfi_code", values="nav")
    returns   = pivot_nav.pct_change().dropna()

    mean_daily  = returns.mean()
    cov_daily   = returns.cov()

    # Annualised equivalents
    mean_ann = mean_daily * 252
    cov_ann  = cov_daily * 252

    print(f"Returns matrix shape: {returns.shape} — {returns.shape[0]} trading days")

    # ── Monte Carlo random portfolios ─────────────────────────────────────────
    np.random.seed(42)
    port_returns  = np.zeros(NUM_PORTFOLIOS)
    port_volatility = np.zeros(NUM_PORTFOLIOS)
    port_sharpe   = np.zeros(NUM_PORTFOLIOS)
    weights_matrix = np.zeros((NUM_PORTFOLIOS, NUM_ASSETS))

    for i in range(NUM_PORTFOLIOS):
        w = np.random.dirichlet(np.ones(NUM_ASSETS))   # sums to exactly 1
        weights_matrix[i] = w

        p_ret = float(mean_ann.values @ w)
        p_vol = float(np.sqrt(w @ cov_ann.values @ w))

        port_returns[i]    = p_ret
        port_volatility[i] = p_vol
        port_sharpe[i]     = (p_ret - RISK_FREE_ANNUAL) / p_vol

    # ── Identify optimal portfolios ───────────────────────────────────────────
    max_sharpe_idx = int(np.argmax(port_sharpe))
    min_vol_idx    = int(np.argmin(port_volatility))

    def allocation_table(weights, label):
        df = pd.DataFrame({
            "Fund": [name_map[c] for c in top_funds],
            "AMFI Code": top_funds,
            "Weight (%)": np.round(weights * 100, 2),
        })
        print(f"\n{'='*70}")
        print(f"  {label}")
        print(f"{'='*70}")
        print(f"  Annualised Return    : {port_returns[max_sharpe_idx if 'Sharpe' in label else min_vol_idx]:.2%}")
        print(f"  Annualised Volatility: {port_volatility[max_sharpe_idx if 'Sharpe' in label else min_vol_idx]:.2%}")
        print(f"  Sharpe Ratio         : {port_sharpe[max_sharpe_idx if 'Sharpe' in label else min_vol_idx]:.4f}")
        print(df.to_string(index=False))

    allocation_table(weights_matrix[max_sharpe_idx], "Maximum Sharpe Ratio Portfolio")
    allocation_table(weights_matrix[min_vol_idx],    "Minimum Volatility Portfolio")

    # ── Plot Efficient Frontier ───────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 8))

    sc = ax.scatter(
        port_volatility, port_returns,
        c=port_sharpe, cmap="YlGnBu",
        marker="o", s=10, alpha=0.4
    )
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Sharpe Ratio", fontsize=11)

    ax.scatter(
        port_volatility[max_sharpe_idx], port_returns[max_sharpe_idx],
        marker="*", color="#E53935", s=600, zorder=5,
        label=f"Max Sharpe  (Sharpe={port_sharpe[max_sharpe_idx]:.2f})"
    )
    ax.scatter(
        port_volatility[min_vol_idx], port_returns[min_vol_idx],
        marker="*", color="#43A047", s=600, zorder=5,
        label=f"Min Volatility  (σ={port_volatility[min_vol_idx]:.2%})"
    )

    ax.set_title("Markowitz Efficient Frontier — Top 5 Funds (10,000 random portfolios)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Annualised Volatility (Std Dev)", fontsize=12)
    ax.set_ylabel("Annualised Expected Return", fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1%}"))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1%}"))
    ax.legend(fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle="--")
    plt.tight_layout()

    OUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight")
    plt.close()

    file_size = os.path.getsize(OUT_IMG)
    assert file_size > 10_000, f"Chart too small ({file_size} bytes)"
    print(f"\n✅ Chart saved → {OUT_IMG}  ({file_size / 1024:.1f} KB)")
    print("✅ Portfolio optimisation complete.")


if __name__ == "__main__":
    run_portfolio_optimisation()
