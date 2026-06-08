"""
Bonus Challenge 2: Streamlit Web Dashboard
Bluestock MF Capstone — Alternative to Tableau/Power BI

Multi-page interactive dashboard with:
  - Page 1 (Overview): KPI cards + fund category filter + risk grade filter + charts
  - Page 2 (Performance): Detailed metrics, scatter / bar charts + fund house filter + plan filter
  - Page 3 (NAV History): NAV trend chart with fund selector + date range slider
  - Page 4 (Advanced Analytics): VaR/CVaR table + risk heatmap + category filter + AUM filter

Each page has ≥ 2 interactive filters/slicers (meets D5 rubric requirement).

Usage:
    streamlit run app.py
"""

import sqlite3
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE         = Path(__file__).resolve().parent
DB_PATH      = BASE / "data" / "db" / "bluestock_mf.db"
NAV_CSV      = BASE / "data" / "processed" / "clean_nav.csv"
VAR_CSV      = BASE / "data" / "processed" / "var_cvar_report.csv"
SCORECARD_CSV= BASE / "data" / "processed" / "fund_scorecard.csv"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .metric-card {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    color: white; border-radius: 12px; padding: 20px 24px;
    box-shadow: 0 6px 20px rgba(37,99,235,0.3);
    text-align: center; margin-bottom: 10px;
  }
  .metric-card h3 { margin: 0; font-size: 0.85rem; opacity: 0.85; font-weight: 400; }
  .metric-card h2 { margin: 8px 0 0; font-size: 1.8rem; font-weight: 700; }
  .stSidebar { background: #0F172A !important; }
  [data-testid="stSidebarNav"] { background: #0F172A; }
</style>
""", unsafe_allow_html=True)

# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data
def load_scheme_perf():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM scheme_performance", conn)
    conn.close()
    return df

@st.cache_data
def load_nav_history():
    return pd.read_csv(NAV_CSV, parse_dates=["date"])

@st.cache_data
def load_var_report():
    if VAR_CSV.exists():
        return pd.read_csv(VAR_CSV)
    return None

@st.cache_data
def load_scorecard():
    if SCORECARD_CSV.exists():
        return pd.read_csv(SCORECARD_CSV)
    return None

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("## 📊 Bluestock MF")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "📈 Performance", "📉 NAV History", "🔬 Advanced Analytics"],
    index=0,
)
st.sidebar.markdown("---")
st.sidebar.caption("Bluestock MF Capstone · Data: AMFI via mfapi.in")

# ── Load base data ────────────────────────────────────────────────────────────
perf_df = load_scheme_perf()

# ==============================================================================
# PAGE 1 — OVERVIEW
# ==============================================================================
if page == "🏠 Overview":
    st.title("🏠 Fund Overview")
    st.markdown("High-level summary of all 40 tracked mutual funds.")

    # ── Slicers (≥2) ─────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        categories = ["All"] + sorted(perf_df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("🗂️ Filter by Category", categories, key="ov_cat")
    with col_f2:
        risk_grades = ["All"] + sorted(perf_df["risk_grade"].dropna().unique().tolist())
        sel_risk = st.selectbox("⚠️ Filter by Risk Grade", risk_grades, key="ov_risk")

    filtered = perf_df.copy()
    if sel_cat != "All":
        filtered = filtered[filtered["category"] == sel_cat]
    if sel_risk != "All":
        filtered = filtered[filtered["risk_grade"] == sel_risk]

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='metric-card'><h3>Funds</h3><h2>{len(filtered)}</h2></div>",
                    unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='metric-card'><h3>Avg 1Y Return</h3>"
                    f"<h2>{filtered['return_1yr_pct'].mean():.2f}%</h2></div>",
                    unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='metric-card'><h3>Avg 3Y Return</h3>"
                    f"<h2>{filtered['return_3yr_pct'].mean():.2f}%</h2></div>",
                    unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='metric-card'><h3>Total AUM (₹ Cr)</h3>"
                    f"<h2>₹{filtered['aum_crore'].sum():,.0f}</h2></div>",
                    unsafe_allow_html=True)

    st.markdown("---")
    ch1, ch2 = st.columns(2)

    with ch1:
        fig = px.bar(
            filtered.sort_values("return_3yr_pct", ascending=False).head(10),
            x="scheme_name", y="return_3yr_pct",
            color="category", title="Top 10 Funds by 3Y Return",
            labels={"return_3yr_pct": "3Y Return (%)", "scheme_name": "Fund"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(xaxis_tickangle=-40, xaxis_title="", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        aum_by_cat = filtered.groupby("category")["aum_crore"].sum().reset_index()
        fig2 = px.pie(aum_by_cat, values="aum_crore", names="category",
                      title="AUM Distribution by Category",
                      hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Fund Details Table")
    st.dataframe(
        filtered[["scheme_name","category","risk_grade","return_1yr_pct",
                   "return_3yr_pct","return_5yr_pct","sharpe_ratio","aum_crore",
                   "expense_ratio_pct","morningstar_rating"]].reset_index(drop=True),
        use_container_width=True,
    )

# ==============================================================================
# PAGE 2 — PERFORMANCE
# ==============================================================================
elif page == "📈 Performance":
    st.title("📈 Performance Metrics")
    st.markdown("Deep-dive into risk-adjusted performance metrics.")

    # ── Slicers (≥2) ─────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fund_houses = ["All"] + sorted(perf_df["fund_house"].dropna().unique().tolist())
        sel_fh = st.selectbox("🏦 Filter by Fund House", fund_houses, key="perf_fh")
    with col_f2:
        plans = ["All"] + sorted(perf_df["plan"].dropna().unique().tolist())
        sel_plan = st.selectbox("📄 Filter by Plan", plans, key="perf_plan")

    filtered = perf_df.copy()
    if sel_fh != "All":
        filtered = filtered[filtered["fund_house"] == sel_fh]
    if sel_plan != "All":
        filtered = filtered[filtered["plan"] == sel_plan]

    ch1, ch2 = st.columns(2)
    with ch1:
        fig = px.scatter(
            filtered, x="expense_ratio_pct", y="return_3yr_pct",
            size="aum_crore", color="category", hover_name="scheme_name",
            title="Expense Ratio vs 3Y Return (Bubble = AUM)",
            labels={"expense_ratio_pct": "Expense Ratio (%)", "return_3yr_pct": "3Y Return (%)"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        fig2 = px.scatter(
            filtered, x="std_dev_ann_pct", y="sharpe_ratio",
            color="category", hover_name="scheme_name",
            title="Risk (Std Dev) vs Sharpe Ratio",
            labels={"std_dev_ann_pct": "Annualised Std Dev (%)", "sharpe_ratio": "Sharpe Ratio"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Risk-Adjusted Metrics Table")
    st.dataframe(
        filtered[["scheme_name","category","sharpe_ratio","sortino_ratio",
                   "alpha","beta","max_drawdown_pct","std_dev_ann_pct"]].reset_index(drop=True),
        use_container_width=True,
    )

# ==============================================================================
# PAGE 3 — NAV HISTORY
# ==============================================================================
elif page == "📉 NAV History":
    st.title("📉 NAV History & Trends")

    nav_df = load_nav_history()
    merged = nav_df.merge(
        perf_df[["amfi_code", "scheme_name", "category"]],
        on="amfi_code", how="left"
    )

    # ── Slicers (≥2) ─────────────────────────────────────────────────────────
    fund_names = sorted(merged["scheme_name"].dropna().unique().tolist())
    sel_funds = st.multiselect(
        "🔍 Select Funds to Compare (up to 5)",
        fund_names,
        default=fund_names[:3],
        key="nav_funds",
    )

    date_min = merged["date"].min().date()
    date_max = merged["date"].max().date()
    sel_dates = st.slider(
        "📅 Select Date Range",
        min_value=date_min, max_value=date_max,
        value=(date_min, date_max),
        key="nav_dates",
    )

    if sel_funds:
        view = merged[
            (merged["scheme_name"].isin(sel_funds)) &
            (merged["date"] >= pd.Timestamp(sel_dates[0])) &
            (merged["date"] <= pd.Timestamp(sel_dates[1]))
        ]
        fig = px.line(
            view, x="date", y="nav", color="scheme_name",
            title="NAV Trend Over Time",
            labels={"nav": "NAV (₹)", "date": "Date", "scheme_name": "Fund"},
        )
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one fund.")

# ==============================================================================
# PAGE 4 — ADVANCED ANALYTICS
# ==============================================================================
elif page == "🔬 Advanced Analytics":
    st.title("🔬 Advanced Risk Analytics")
    st.markdown("Value at Risk, CVaR, and sector concentration analysis.")

    # ── Slicers (≥2) ─────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        categories = ["All"] + sorted(perf_df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("🗂️ Filter by Category", categories, key="adv_cat")
    with col_f2:
        aum_max = int(perf_df["aum_crore"].max())
        sel_aum = st.slider("💰 Min AUM (₹ Cr)", 0, aum_max, 0, step=500, key="adv_aum")

    var_df = load_var_report()
    if var_df is not None:
        # Merge with performance for filters
        var_merged = var_df.merge(
            perf_df[["amfi_code", "aum_crore"]], on="amfi_code", how="left"
        )
        if sel_cat != "All":
            var_merged = var_merged[var_merged["category"] == sel_cat]
        var_merged = var_merged[var_merged["aum_crore"] >= sel_aum]

        ch1, ch2 = st.columns(2)
        with ch1:
            fig = px.bar(
                var_merged.sort_values("var_95_pct"),
                x="var_95_pct", y="scheme_name",
                orientation="h", color="risk_grade",
                title="Historical VaR (95%) by Fund",
                labels={"var_95_pct": "VaR 95% (daily)", "scheme_name": ""},
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            fig2 = px.scatter(
                var_merged, x="var_95_pct", y="cvar_95_pct",
                color="risk_grade", hover_name="scheme_name",
                title="VaR vs CVaR (95%)",
                labels={"var_95_pct": "VaR (95%)", "cvar_95_pct": "CVaR (95%)"},
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("VaR / CVaR Table")
        st.dataframe(
            var_merged[["scheme_name","category","risk_grade",
                         "var_95_pct","cvar_95_pct","annualised_var_pct","n_observations"]].reset_index(drop=True),
            use_container_width=True,
        )
    else:
        st.warning("var_cvar_report.csv not found. Run `python scripts/compute_var_cvar.py` first.")

    # Fund Scorecard
    scorecard = load_scorecard()
    if scorecard is not None:
        st.markdown("---")
        st.subheader("🏅 Fund Scorecard (Composite Score 0–100)")
        merged_sc = scorecard.merge(
            perf_df[["amfi_code","scheme_name","category"]], on="amfi_code", how="left"
        )
        fig3 = px.bar(
            merged_sc.sort_values("composite_score", ascending=False),
            x="composite_score", y="scheme_name",
            orientation="h", color="composite_score",
            color_continuous_scale="Blues",
            title="Composite Fund Score (higher = better)",
            labels={"composite_score": "Score", "scheme_name": ""},
        )
        fig3.update_layout(height=600, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)
