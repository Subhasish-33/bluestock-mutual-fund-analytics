"""
Fund Recommender Engine
Bluestock MF Capstone | Day 6

Input:  investor risk_appetite ('Low' | 'Moderate' | 'High')
Logic:  Filter clean_performance.csv by matching risk_grade categories,
        sort by sharpe_ratio descending, return Top 3 funds.
Output: Printed recommendation table
"""

import pandas as pd
import os
import sys

# ── Risk Grade Mapping ─────────────────────────────────────────────────────────
RISK_MAP = {
    "Low":      ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High"],
}


class FundRecommender:
    """Recommender system for mutual funds based on investor risk profile."""

    def __init__(self, perf_df: pd.DataFrame, scorecard_df: pd.DataFrame):
        """
        Initialise with fund performance and scorecard DataFrames.

        Parameters
        ----------
        perf_df      : clean_performance.csv loaded as DataFrame
        scorecard_df : fund_scorecard.csv loaded as DataFrame
        """
        self.perf_df = perf_df.copy()
        self.scorecard_df = scorecard_df.copy()

        # Merge scorecard Sharpe (computed from NAV) into perf for consistency
        # Use perf sharpe_ratio as primary (already in clean_performance.csv)
        self._validate()

    def _validate(self):
        required_perf = {"amfi_code", "scheme_name", "category", "risk_grade",
                         "sharpe_ratio", "return_3yr_pct"}
        required_scorecard = {"amfi_code", "composite_score"}
        missing_perf = required_perf - set(self.perf_df.columns)
        missing_score = required_scorecard - set(self.scorecard_df.columns)
        if missing_perf:
            raise ValueError(f"clean_performance.csv missing columns: {missing_perf}")
        if missing_score:
            raise ValueError(f"fund_scorecard.csv missing columns: {missing_score}")

    def get_recommendations(self, risk_profile: str) -> pd.DataFrame:
        """
        Get top-3 fund recommendations for a given risk profile.

        Parameters
        ----------
        risk_profile : str — one of 'Low', 'Moderate', 'High'

        Returns
        -------
        DataFrame with columns: Rank, Scheme Name, Sharpe Ratio,
                                 3yr Return (%), Category, Risk Grade
        """
        risk_profile = risk_profile.strip().title()
        if risk_profile not in RISK_MAP:
            raise ValueError(
                f"Invalid risk_profile '{risk_profile}'. "
                f"Choose from: {list(RISK_MAP.keys())}"
            )

        matching_grades = RISK_MAP[risk_profile]

        # Filter by matching risk grades
        filtered = self.perf_df[
            self.perf_df["risk_grade"].isin(matching_grades)
        ].copy()

        if filtered.empty:
            raise ValueError(
                f"No funds found for risk profile '{risk_profile}' "
                f"(grades: {matching_grades})"
            )

        # Sort by sharpe_ratio descending, take top 3
        top3 = (
            filtered
            .sort_values("sharpe_ratio", ascending=False)
            .head(3)
            .reset_index(drop=True)
        )

        # Build result table
        result = pd.DataFrame({
            "Rank":             top3.index + 1,
            "Scheme Name":      top3["scheme_name"],
            "Sharpe Ratio":     top3["sharpe_ratio"].round(4),
            "3yr Return (%)":   top3["return_3yr_pct"].round(2),
            "Category":         top3["category"],
            "Risk Grade":       top3["risk_grade"],
        })

        return result

    def print_recommendation_table(self, risk_profile: str) -> None:
        """Pretty-print the recommendation table to stdout."""
        try:
            recommendations = self.get_recommendations(risk_profile)
        except ValueError as e:
            print(f"[ERROR] {e}")
            return

        print(f"\n{'='*70}")
        print(f"  💼 FUND RECOMMENDATIONS — Risk Profile: {risk_profile.upper()}")
        print(f"{'='*70}")
        print(f"  Matching Risk Grades: {', '.join(RISK_MAP[risk_profile.title()])}")
        print(f"  Ranked by: Sharpe Ratio (highest first)")
        print(f"{'='*70}")

        for _, row in recommendations.iterrows():
            print(f"\n  Rank #{int(row['Rank'])}")
            print(f"  Fund   : {row['Scheme Name']}")
            print(f"  Sharpe : {row['Sharpe Ratio']:.4f}")
            print(f"  3yr Ret: {row['3yr Return (%)']:.2f}%")
            print(f"  Type   : {row['Category']} ({row['Risk Grade']})")

        print(f"\n{'='*70}\n")

    def score_fund(self, amfi_code: int, criteria: dict) -> float:
        """
        Score a fund based on custom criteria weights.

        Parameters
        ----------
        amfi_code : int  — AMFI fund code
        criteria  : dict — e.g. {'sharpe_ratio': 0.5, 'cagr_3yr': 0.5}

        Returns
        -------
        float — weighted score
        """
        row = self.scorecard_df[self.scorecard_df["amfi_code"] == amfi_code]
        if row.empty:
            return 0.0

        score = 0.0
        for metric, weight in criteria.items():
            if metric in row.columns:
                score += float(row.iloc[0][metric]) * weight
        return round(score, 4)


# ── Main Entry Point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Resolve data paths relative to this script's location
    base_dir     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    perf_path    = os.path.join(base_dir, "data", "processed", "clean_performance.csv")
    score_path   = os.path.join(base_dir, "data", "processed", "fund_scorecard.csv")

    # Load data
    print("Loading fund data ...")
    perf_df      = pd.read_csv(perf_path)
    scorecard_df = pd.read_csv(score_path)

    # Instantiate recommender
    recommender = FundRecommender(perf_df, scorecard_df)

    # Print recommendations for all three risk profiles
    for profile in ["Low", "Moderate", "High"]:
        recommender.print_recommendation_table(profile)

    # Example: Score a specific fund with custom weights
    sample_code = 148567  # Mirae Asset Large Cap
    custom_score = recommender.score_fund(
        sample_code,
        criteria={"sharpe_ratio": 0.5, "cagr_3yr": 0.3, "alpha": 0.2}
    )
    print(f"Custom score for AMFI {sample_code}: {custom_score}")
    print("\n✅ recommender.py executed successfully.")
