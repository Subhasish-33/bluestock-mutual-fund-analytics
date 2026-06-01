"""
Compute Performance Metrics

This module computes financial metrics: Sharpe ratio, CAGR, Beta, VaR
"""

import pandas as pd
import numpy as np


def compute_sharpe_ratio(returns, risk_free_rate=0.02):
    """Compute Sharpe ratio."""
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std()


def compute_cagr(initial_value, final_value, num_years):
    """Compute Compound Annual Growth Rate."""
    return (final_value / initial_value) ** (1 / num_years) - 1


def compute_beta(fund_returns, market_returns):
    """Compute Beta against market benchmark."""
    covariance = np.cov(fund_returns, market_returns)[0][1]
    market_variance = np.var(market_returns)
    return covariance / market_variance


def compute_var(returns, confidence_level=0.95):
    """Compute Value at Risk."""
    return np.percentile(returns, (1 - confidence_level) * 100)


if __name__ == "__main__":
    print("Computing performance metrics...")
