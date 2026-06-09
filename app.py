"""
Bonus Challenge 2: Streamlit Web Dashboard — PREMIUM EDITION
Bluestock MF Capstone — Dashboard 2.0

5-page premium dark finance dashboard:
  - Page 1 (Command Center): Glassmorphism KPIs, treemap, lollipop chart, styled table
  - Page 2 (Alpha Lab): Quadrant analysis, radar/spider chart, fund comparison
  - Page 3 (Time Machine): Indexed NAV chart + live Returns Calculator
  - Page 4 (Risk Intelligence): Heatmap, VaR/CVaR charts, leaderboard
  - Page 5 (Fund Finder): AI-style weighted scoring recommendation engine

Usage:
    streamlit run app.py
"""

import sqlite3
import math
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).resolve().parent
DB_PATH       = BASE / "data" / "db" / "bluestock_mf.db"
NAV_CSV       = BASE / "data" / "processed" / "clean_nav.csv"
VAR_CSV       = BASE / "data" / "processed" / "var_cvar_report.csv"
SCORECARD_CSV = BASE / "data" / "processed" / "fund_scorecard.csv"

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL THEME & CSS
# ══════════════════════════════════════════════════════════════════════════════
ACCENT     = "#00D4FF"   # electric teal
GOLD       = "#FFD700"   # top performers
BG_DARK    = "#050E1F"   # page background
BG_CARD    = "rgba(255,255,255,0.04)"
BORDER     = "rgba(0,212,255,0.18)"
GREEN      = "#00E676"
RED        = "#FF5252"
TEXT_MAIN  = "#E8F4FD"
TEXT_SUB   = "#8BA3C7"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── Reset & base ───────────────────────────────────────────────────────── */
  html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif;
    background-color: {BG_DARK};
    color: {TEXT_MAIN};
  }}

  /* ── Hide Streamlit chrome ──────────────────────────────────────────────── */
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

  /* ── Sidebar ────────────────────────────────────────────────────────────── */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #070F22 0%, #0A1628 100%) !important;
    border-right: 1px solid {BORDER};
  }}
  [data-testid="stSidebar"] * {{ color: {TEXT_MAIN} !important; }}

  /* ── Radio buttons → nav pills ──────────────────────────────────────────── */
  [data-testid="stSidebar"] .stRadio > label {{
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {TEXT_SUB} !important;
  }}
  [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    display: block;
    padding: 10px 16px;
    border-radius: 8px;
    margin: 3px 0;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 0.95rem;
    font-weight: 500;
  }}
  [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: rgba(0,212,255,0.08);
  }}

  /* ── Glass card ─────────────────────────────────────────────────────────── */
  .glass-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 22px 26px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin-bottom: 16px;
    transition: border-color 0.3s;
  }}
  .glass-card:hover {{ border-color: rgba(0,212,255,0.4); }}

  /* ── KPI card ───────────────────────────────────────────────────────────── */
  .kpi-card {{
    background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,212,255,0.02) 100%);
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
  }}
  .kpi-card:hover {{ transform: translateY(-3px); border-color: {ACCENT}; }}
  .kpi-card::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, {ACCENT}, transparent);
  }}
  .kpi-label {{
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: {TEXT_SUB}; margin-bottom: 8px;
  }}
  .kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem; font-weight: 700; color: {TEXT_MAIN};
    line-height: 1.1;
  }}
  .kpi-delta-pos {{ font-size: 0.8rem; color: {GREEN}; margin-top: 5px; }}
  .kpi-delta-neg {{ font-size: 0.8rem; color: {RED};   margin-top: 5px; }}

  /* ── Fund card (Fund Finder) ─────────────────────────────────────────────── */
  .fund-card {{
    background: linear-gradient(135deg, rgba(0,212,255,0.06), rgba(5,14,31,0.9));
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 12px;
    position: relative;
    transition: border-color 0.25s, transform 0.25s;
  }}
  .fund-card:hover {{ border-color: {ACCENT}; transform: translateX(4px); }}
  .fund-rank {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem; font-weight: 800; color: {ACCENT};
    opacity: 0.25; position: absolute; top: 12px; right: 18px;
  }}
  .fund-name {{ font-size: 1.05rem; font-weight: 700; color: {TEXT_MAIN}; margin-bottom: 4px; }}
  .fund-meta {{ font-size: 0.82rem; color: {TEXT_SUB}; margin-bottom: 10px; }}
  .fund-score-bar-bg {{
    background: rgba(255,255,255,0.08); border-radius: 99px; height: 6px; margin: 8px 0;
  }}
  .fund-score-bar {{
    height: 6px; border-radius: 99px;
    background: linear-gradient(90deg, {ACCENT}, #0080FF);
  }}
  .badge {{
    display: inline-block; font-size: 0.72rem; font-weight: 600;
    padding: 3px 10px; border-radius: 99px; margin-right: 6px; margin-top: 4px;
  }}
  .badge-green  {{ background: rgba(0,230,118,0.15); color: {GREEN}; border: 1px solid rgba(0,230,118,0.3); }}
  .badge-teal   {{ background: rgba(0,212,255,0.12); color: {ACCENT}; border: 1px solid {BORDER}; }}
  .badge-gold   {{ background: rgba(255,215,0,0.12); color: {GOLD};  border: 1px solid rgba(255,215,0,0.3); }}
  .badge-red    {{ background: rgba(255,82,82,0.12);  color: {RED};   border: 1px solid rgba(255,82,82,0.3); }}

  /* ── Page title ─────────────────────────────────────────────────────────── */
  .page-title {{
    font-size: 2rem; font-weight: 800; color: {TEXT_MAIN};
    letter-spacing: -0.02em; margin-bottom: 2px;
  }}
  .page-subtitle {{
    font-size: 0.9rem; color: {TEXT_SUB}; margin-bottom: 24px;
  }}

  /* ── Dataframe ──────────────────────────────────────────────────────────── */
  [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}

  /* ── Selectbox / slider ─────────────────────────────────────────────────── */
  .stSelectbox > div > div {{ background: rgba(255,255,255,0.04) !important; border-color: {BORDER} !important; border-radius: 8px !important; }}
  .stMultiSelect > div > div {{ background: rgba(255,255,255,0.04) !important; border-color: {BORDER} !important; border-radius: 8px !important; }}

  /* ── Section divider ────────────────────────────────────────────────────── */
  .section-sep {{ border: none; border-top: 1px solid {BORDER}; margin: 24px 0; }}

  /* ── Glow text ──────────────────────────────────────────────────────────── */
  .glow {{ color: {ACCENT}; text-shadow: 0 0 20px rgba(0,212,255,0.5); }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLOTLY GLOBAL TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(family="Outfit, sans-serif", color=TEXT_MAIN, size=12),
    title_font=dict(family="Outfit, sans-serif", size=15, color=TEXT_MAIN),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color=TEXT_SUB, size=11),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color=TEXT_SUB, size=11),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, borderwidth=1,
        font=dict(color=TEXT_MAIN, size=11),
    ),
    margin=dict(l=10, r=10, t=45, b=10),
    hoverlabel=dict(
        bgcolor="#0A1628", bordercolor=BORDER,
        font=dict(family="Outfit", color=TEXT_MAIN),
    ),
)

QUALITATIVE = ["#00D4FF", "#0080FF", "#7C3AED", "#FFD700", "#00E676",
               "#FF5252", "#FF9100", "#E040FB", "#00BCD4", "#64FFDA"]

def apply_theme(fig, height=420):
    """Apply the global dark finance theme to any Plotly figure."""
    fig.update_layout(**CHART_LAYOUT, height=height)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADERS
# ══════════════════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def kpi_card(label, value, delta=None, prefix="", suffix=""):
    """Render a premium KPI card."""
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f"<div class='{cls}'>{arrow} {abs(delta):.2f}%</div>"
    return f"""
    <div class='kpi-card'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{prefix}{value}{suffix}</div>
      {delta_html}
    </div>"""

def section_header(title, subtitle=""):
    st.markdown(f"<div class='page-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

def stars(rating):
    return "⭐" * int(rating) + "☆" * (5 - int(rating))


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 20px 0 10px;'>
      <div style='font-size:2rem;'>💹</div>
      <div style='font-size:1.15rem; font-weight:800; color:{TEXT_MAIN}; letter-spacing:-0.02em;'>
        Bluestock MF
      </div>
      <div style='font-size:0.75rem; color:{TEXT_SUB}; letter-spacing:0.1em; text-transform:uppercase;'>
        Analytics Platform
      </div>
    </div>
    <hr style='border-color:{BORDER}; margin: 10px 0 18px;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🖥️  Command Center",
         "🧪  Alpha Lab",
         "📅  Time Machine",
         "🛡️  Risk Intelligence",
         "🤖  Fund Finder"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown(f"""
    <hr style='border-color:{BORDER}; margin: 18px 0 10px;'>
    <div style='font-size:0.72rem; color:{TEXT_SUB}; text-align:center; line-height:1.7;'>
      Data: AMFI · mfapi.in<br>
      Bluestock Fintech MJ28<br>
      <span style='color:{ACCENT}'>● LIVE</span>
    </div>
    """, unsafe_allow_html=True)


# ── Load base data ─────────────────────────────────────────────────────────────
perf_df = load_scheme_perf()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — COMMAND CENTER
# ══════════════════════════════════════════════════════════════════════════════
if page == "🖥️  Command Center":
    section_header("🖥️ Command Center", "Real-time overview across all 40 tracked mutual funds")

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        categories = ["All"] + sorted(perf_df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", categories, key="ov_cat")
    with col_f2:
        risk_grades = ["All"] + sorted(perf_df["risk_grade"].dropna().unique().tolist())
        sel_risk = st.selectbox("Risk Grade", risk_grades, key="ov_risk")
    with col_f3:
        ratings = ["All"] + sorted(perf_df["morningstar_rating"].dropna().unique().tolist(), reverse=True)
        sel_rating = st.selectbox("Min Morningstar Rating", ratings, key="ov_rating")

    filtered = perf_df.copy()
    if sel_cat   != "All": filtered = filtered[filtered["category"]           == sel_cat]
    if sel_risk  != "All": filtered = filtered[filtered["risk_grade"]         == sel_risk]
    if sel_rating!= "All": filtered = filtered[filtered["morningstar_rating"] >= int(sel_rating)]

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    cards = [
        (k1, "Funds Tracked",      f"{len(filtered)}",                        None),
        (k2, "Avg 1Y Return",      f"{filtered['return_1yr_pct'].mean():.2f}", filtered['return_1yr_pct'].mean(), "%"),
        (k3, "Avg 3Y Return",      f"{filtered['return_3yr_pct'].mean():.2f}", filtered['return_3yr_pct'].mean(), "%"),
        (k4, "Avg Sharpe",         f"{filtered['sharpe_ratio'].mean():.2f}",   None),
        (k5, "Total AUM",          f"₹{filtered['aum_crore'].sum():,.0f}",     None),
        (k6, "Avg Expense Ratio",  f"{filtered['expense_ratio_pct'].mean():.2f}",None),
    ]
    for col, label, val, delta, *suf in [(c[0],c[1],c[2],c[3]) for c in cards]:
        with col:
            st.markdown(kpi_card(label, val), unsafe_allow_html=True)

    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────────────────────
    ch1, ch2 = st.columns([3, 2])

    with ch1:
        # Lollipop chart — Top 10 funds by 3Y return
        top10 = filtered.nlargest(10, "return_3yr_pct").sort_values("return_3yr_pct")
        short_names = top10["scheme_name"].apply(lambda x: x[:28] + "…" if len(x) > 28 else x)

        fig_lollipop = go.Figure()
        fig_lollipop.add_trace(go.Scatter(
            x=top10["return_3yr_pct"], y=short_names,
            mode="markers",
            marker=dict(size=14, color=ACCENT,
                        line=dict(color="#FFFFFF", width=2)),
            hovertemplate="<b>%{y}</b><br>3Y Return: %{x:.2f}%<extra></extra>",
        ))
        for i, (ret, name) in enumerate(zip(top10["return_3yr_pct"], short_names)):
            fig_lollipop.add_shape(type="line",
                x0=0, x1=ret, y0=i, y1=i,
                line=dict(color=ACCENT, width=2, dash="dot"))
        apply_theme(fig_lollipop, height=400)
        fig_lollipop.update_layout(
            title="🏆 Top 10 Funds — 3Y Return (%)",
            xaxis_title="3Y Return (%)",
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_lollipop, use_container_width=True)

    with ch2:
        # Treemap — AUM by category
        aum_cat = filtered.groupby("category")["aum_crore"].sum().reset_index()
        fig_tree = px.treemap(
            aum_cat, path=["category"], values="aum_crore",
            color="aum_crore", color_continuous_scale=["#050E1F", "#0080FF", "#00D4FF"],
            title="💰 AUM Distribution by Category",
        )
        fig_tree.update_traces(
            textfont=dict(family="Outfit", size=13, color="white"),
            hovertemplate="<b>%{label}</b><br>AUM: ₹%{value:,.0f} Cr<extra></extra>",
        )
        apply_theme(fig_tree, height=400)
        fig_tree.update_layout(coloraxis_showscale=False, margin=dict(l=0,r=0,t=45,b=0))
        st.plotly_chart(fig_tree, use_container_width=True)

    # ── Styled Fund Table ──────────────────────────────────────────────────────
    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:10px;color:{TEXT_MAIN}'>📋 Fund Details</div>", unsafe_allow_html=True)
    display_cols = ["scheme_name", "category", "risk_grade", "morningstar_rating",
                    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                    "sharpe_ratio", "aum_crore", "expense_ratio_pct"]
    tbl = filtered[display_cols].copy()
    tbl["morningstar_rating"] = tbl["morningstar_rating"].apply(stars)
    tbl.columns = ["Fund", "Category", "Risk", "Rating",
                   "1Y Ret%", "3Y Ret%", "5Y Ret%", "Sharpe", "AUM (Cr)", "ER%"]
    st.dataframe(
        tbl.style
          .background_gradient(subset=["3Y Ret%","5Y Ret%"], cmap="Blues")
          .format({"1Y Ret%":"{:.2f}","3Y Ret%":"{:.2f}","5Y Ret%":"{:.2f}",
                   "Sharpe":"{:.2f}","AUM (Cr)":"{:,.0f}","ER%":"{:.2f}"}),
        use_container_width=True, height=350,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ALPHA LAB
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪  Alpha Lab":
    section_header("🧪 Alpha Lab", "Deep-dive into risk-adjusted performance — identify the true stars")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        fund_houses = ["All"] + sorted(perf_df["fund_house"].dropna().unique().tolist())
        sel_fh = st.selectbox("Fund House", fund_houses, key="perf_fh")
    with col_f2:
        plans = ["All"] + sorted(perf_df["plan"].dropna().unique().tolist())
        sel_plan = st.selectbox("Plan", plans, key="perf_plan")
    with col_f3:
        categories = ["All"] + sorted(perf_df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", categories, key="perf_cat")

    filtered = perf_df.copy()
    if sel_fh   != "All": filtered = filtered[filtered["fund_house"] == sel_fh]
    if sel_plan != "All": filtered = filtered[filtered["plan"]       == sel_plan]
    if sel_cat  != "All": filtered = filtered[filtered["category"]   == sel_cat]

    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)

    # ── Quadrant Chart ─────────────────────────────────────────────────────────
    st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:4px;color:{TEXT_MAIN}'>📊 Quadrant Analysis — Return vs Risk</div>", unsafe_allow_html=True)
    st.caption("Stars: High Return + Low Risk · Question Marks: High Return + High Risk · Cash Cows: Low Return + Low Risk · Dogs: Low Return + High Risk")

    med_ret = filtered["return_3yr_pct"].median()
    med_std = filtered["std_dev_ann_pct"].median()

    def quadrant(row):
        hi_ret = row["return_3yr_pct"] >= med_ret
        lo_std = row["std_dev_ann_pct"] < med_std
        if hi_ret and lo_std:     return "⭐ Stars"
        elif hi_ret and not lo_std: return "❓ Question Marks"
        elif not hi_ret and lo_std: return "🐄 Cash Cows"
        else:                       return "🐕 Dogs"

    filtered = filtered.copy()
    filtered["Quadrant"] = filtered.apply(quadrant, axis=1)

    fig_quad = px.scatter(
        filtered, x="std_dev_ann_pct", y="return_3yr_pct",
        color="Quadrant", size="aum_crore",
        hover_name="scheme_name",
        hover_data={"std_dev_ann_pct":":.2f","return_3yr_pct":":.2f","aum_crore":":.0f"},
        color_discrete_map={
            "⭐ Stars": GREEN, "❓ Question Marks": GOLD,
            "🐄 Cash Cows": ACCENT, "🐕 Dogs": RED,
        },
        labels={"std_dev_ann_pct":"Annualised Std Dev (%)","return_3yr_pct":"3Y Return (%)"},
    )
    # Quadrant lines
    fig_quad.add_hline(y=med_ret, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig_quad.add_vline(x=med_std, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    apply_theme(fig_quad, height=480)
    fig_quad.update_layout(title="Return vs Risk Quadrant Map (bubble = AUM)")
    st.plotly_chart(fig_quad, use_container_width=True)

    # ── Spider / Radar Chart ───────────────────────────────────────────────────
    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:4px;color:{TEXT_MAIN}'>🕸️ Fund Comparison Radar</div>", unsafe_allow_html=True)
    fund_names = sorted(filtered["scheme_name"].dropna().unique().tolist())
    sel_radar = st.multiselect("Select 2-4 Funds to Compare", fund_names,
                               default=fund_names[:3], max_selections=4, key="radar_funds")

    if len(sel_radar) >= 2:
        metrics = ["return_1yr_pct", "return_3yr_pct", "sharpe_ratio", "sortino_ratio", "alpha"]
        metric_labels = ["1Y Return", "3Y Return", "Sharpe", "Sortino", "Alpha"]

        fig_radar = go.Figure()
        for i, fname in enumerate(sel_radar):
            row = filtered[filtered["scheme_name"] == fname].iloc[0]
            # Normalize each metric 0→1 within the filtered set
            vals = []
            for m in metrics:
                mn, mx = filtered[m].min(), filtered[m].max()
                v = (row[m] - mn) / (mx - mn + 1e-9)
                vals.append(round(v, 3))
            vals_closed = vals + [vals[0]]
            labels_closed = metric_labels + [metric_labels[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_closed, theta=labels_closed,
                fill="toself", name=fname[:30],
                line=dict(color=QUALITATIVE[i], width=2),
                fillcolor=f"rgba({int(QUALITATIVE[i][1:3],16)},{int(QUALITATIVE[i][3:5],16)},{int(QUALITATIVE[i][5:7],16)},0.1)",
            ))
        apply_theme(fig_radar, height=420)
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(255,255,255,0.02)",
                radialaxis=dict(visible=True, range=[0,1],
                                gridcolor="rgba(255,255,255,0.08)",
                                tickfont=dict(color=TEXT_SUB, size=9)),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                                 tickfont=dict(color=TEXT_MAIN, size=11)),
            ),
            title="Normalized Multi-Metric Radar (higher = better)",
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Select at least 2 funds to render the radar chart.")

    # ── Metrics Table ─────────────────────────────────────────────────────────
    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:8px;color:{TEXT_MAIN}'>📋 Risk-Adjusted Metrics</div>", unsafe_allow_html=True)
    tbl = filtered[["scheme_name","category","sharpe_ratio","sortino_ratio",
                    "alpha","beta","max_drawdown_pct","std_dev_ann_pct"]].copy()
    tbl.columns = ["Fund","Category","Sharpe","Sortino","Alpha","Beta","Max DD%","Std Dev%"]
    st.dataframe(
        tbl.style
          .background_gradient(subset=["Sharpe","Sortino"], cmap="Greens")
          .background_gradient(subset=["Max DD%"], cmap="Reds_r")
          .format({"Sharpe":"{:.2f}","Sortino":"{:.2f}","Alpha":"{:.2f}",
                   "Beta":"{:.2f}","Max DD%":"{:.2f}","Std Dev%":"{:.2f}"}),
        use_container_width=True, height=320,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TIME MACHINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅  Time Machine":
    section_header("📅 Time Machine", "Travel back in time to compare fund journeys and model your returns")

    nav_df = load_nav_history()
    merged = nav_df.merge(
        perf_df[["amfi_code", "scheme_name", "category", "risk_grade"]],
        on="amfi_code", how="left"
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        fund_names = sorted(merged["scheme_name"].dropna().unique().tolist())
        sel_funds = st.multiselect(
            "Select Funds to Compare (max 5)",
            fund_names, default=fund_names[:3], max_selections=5, key="nav_funds",
        )
    with col_f2:
        date_min = merged["date"].min().date()
        date_max = merged["date"].max().date()

    sel_dates = st.slider(
        "Date Range",
        min_value=date_min, max_value=date_max,
        value=(date_min, date_max), key="nav_dates",
    )

    if not sel_funds:
        st.info("Select at least one fund to continue.")
        st.stop()

    view = merged[
        (merged["scheme_name"].isin(sel_funds)) &
        (merged["date"] >= pd.Timestamp(sel_dates[0])) &
        (merged["date"] <= pd.Timestamp(sel_dates[1]))
    ].copy()

    # ── Indexed NAV (rebased to 100) ──────────────────────────────────────────
    indexed = []
    for fname in sel_funds:
        fd = view[view["scheme_name"] == fname].sort_values("date")
        if fd.empty: continue
        base = fd["nav"].iloc[0]
        fd = fd.copy()
        fd["nav_indexed"] = fd["nav"] / base * 100
        indexed.append(fd)

    if indexed:
        idx_df = pd.concat(indexed)
        fig_nav = px.line(
            idx_df, x="date", y="nav_indexed", color="scheme_name",
            labels={"nav_indexed": "Indexed NAV (Base=100)", "date": "Date", "scheme_name": "Fund"},
            color_discrete_sequence=QUALITATIVE,
        )
        fig_nav.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                          annotation_text="Start (100)", annotation_position="bottom right",
                          annotation_font_color=TEXT_SUB)
        apply_theme(fig_nav, height=420)
        fig_nav.update_layout(
            title="📈 Indexed NAV Comparison (all funds start at 100 — apples-to-apples)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        st.plotly_chart(fig_nav, use_container_width=True)

    # ── Returns Calculator ─────────────────────────────────────────────────────
    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:4px;color:{TEXT_MAIN}'>💰 Returns Calculator — What Would Your Investment Be Worth Today?</div>", unsafe_allow_html=True)

    inv_amt = st.number_input("Investment Amount (₹)", min_value=1000, max_value=10_000_000,
                               value=10000, step=1000, key="inv_amt")

    calc_cols = st.columns(len(sel_funds))
    for i, fname in enumerate(sel_funds):
        fd = view[view["scheme_name"] == fname].sort_values("date")
        if fd.empty: continue
        nav_start = fd["nav"].iloc[0]
        nav_end   = fd["nav"].iloc[-1]
        multiplier = nav_end / nav_start
        final_val  = inv_amt * multiplier
        gain       = final_val - inv_amt
        gain_pct   = (multiplier - 1) * 100
        color      = GREEN if gain >= 0 else RED
        arrow      = "▲" if gain >= 0 else "▼"
        with calc_cols[i]:
            st.markdown(f"""
            <div class='glass-card' style='text-align:center;'>
              <div style='font-size:0.78rem;font-weight:600;color:{TEXT_SUB};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;'>
                {fname[:22]}…
              </div>
              <div style='font-family:"JetBrains Mono",monospace;font-size:1.5rem;font-weight:700;color:{TEXT_MAIN};'>
                ₹{final_val:,.0f}
              </div>
              <div style='color:{color};font-size:0.88rem;margin-top:4px;'>
                {arrow} ₹{abs(gain):,.0f} ({gain_pct:+.1f}%)
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — RISK INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛡️  Risk Intelligence":
    section_header("🛡️ Risk Intelligence", "Advanced tail-risk and concentration analytics")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        categories = ["All"] + sorted(perf_df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", categories, key="adv_cat")
    with col_f2:
        risk_grades = ["All"] + sorted(perf_df["risk_grade"].dropna().unique().tolist())
        sel_risk = st.selectbox("Risk Grade", risk_grades, key="adv_risk")
    with col_f3:
        aum_max = int(perf_df["aum_crore"].max())
        sel_aum = st.slider("Min AUM (₹ Cr)", 0, aum_max, 0, step=500, key="adv_aum")

    var_df = load_var_report()
    if var_df is None:
        st.error("var_cvar_report.csv not found. Run `python scripts/compute_var_cvar.py` first.")
        st.stop()

    var_merged = var_df.merge(perf_df[["amfi_code","aum_crore"]], on="amfi_code", how="left")
    if sel_cat  != "All": var_merged = var_merged[var_merged["category"]  == sel_cat]
    if sel_risk != "All": var_merged = var_merged[var_merged["risk_grade"] == sel_risk]
    var_merged = var_merged[var_merged["aum_crore"] >= sel_aum]

    # ── Risk Heatmap ──────────────────────────────────────────────────────────
    heatmap_df = var_merged[["scheme_name","var_95_pct","cvar_95_pct","annualised_var_pct"]].copy()
    heatmap_df = heatmap_df.set_index("scheme_name")

    # Normalize 0→1 for heatmap coloring
    hm_norm = (heatmap_df - heatmap_df.min()) / (heatmap_df.max() - heatmap_df.min() + 1e-9)

    fig_heat = go.Figure(go.Heatmap(
        z=hm_norm.values,
        x=["VaR 95%", "CVaR 95%", "Annualised VaR"],
        y=[n[:30] for n in hm_norm.index],
        colorscale=[[0,"#0A1628"],[0.5,"#0040A0"],[1,"#FF5252"]],
        hovertemplate=(
            "<b>%{y}</b><br>%{x}: %{z:.3f} (normalised)<extra></extra>"
        ),
        showscale=True,
        colorbar=dict(
            title=dict(text="Risk Level", font=dict(color=TEXT_SUB)),
            tickfont=dict(color=TEXT_SUB)
        ),
    ))
    apply_theme(fig_heat, height=max(350, len(hm_norm) * 22))
    fig_heat.update_layout(title="🌡️ Risk Heatmap — VaR & CVaR Across Funds",
                            yaxis=dict(tickfont=dict(size=9)))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)
    with ch1:
        top_var = var_merged.sort_values("var_95_pct").head(15)
        short   = top_var["scheme_name"].apply(lambda x: x[:25] + "…" if len(x) > 25 else x)
        fig_v = go.Figure(go.Bar(
            x=top_var["var_95_pct"], y=short,
            orientation="h",
            marker=dict(
                color=top_var["var_95_pct"],
                colorscale=[[0, GREEN],[0.5, ACCENT],[1, RED]],
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>VaR 95%: %{x:.4f}<extra></extra>",
        ))
        apply_theme(fig_v, height=420)
        fig_v.update_layout(title="Historical VaR (95%) — Lowest to Highest",
                            xaxis_title="VaR (daily)", yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig_v, use_container_width=True)

    with ch2:
        fig_vc = px.scatter(
            var_merged, x="var_95_pct", y="cvar_95_pct",
            color="risk_grade", hover_name="scheme_name", size="aum_crore",
            color_discrete_sequence=QUALITATIVE,
            labels={"var_95_pct":"VaR (95%)","cvar_95_pct":"CVaR (95%)"},
        )
        fig_vc.add_shape(type="line",
            x0=var_merged["var_95_pct"].min(), y0=var_merged["cvar_95_pct"].min(),
            x1=var_merged["var_95_pct"].max(), y1=var_merged["cvar_95_pct"].max(),
            line=dict(color="rgba(255,255,255,0.15)", dash="dot"),
        )
        apply_theme(fig_vc, height=420)
        fig_vc.update_layout(title="VaR vs CVaR — Tail Risk Map")
        st.plotly_chart(fig_vc, use_container_width=True)

    # ── Fund Leaderboard ───────────────────────────────────────────────────────
    scorecard = load_scorecard()
    if scorecard is not None:
        st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:10px;color:{TEXT_MAIN}'>🏅 Fund Leaderboard — Composite Score</div>", unsafe_allow_html=True)
        lb = scorecard.merge(perf_df[["amfi_code","scheme_name","category","risk_grade"]], on="amfi_code", how="left")
        lb = lb.sort_values("composite_score", ascending=False).reset_index(drop=True)

        colors = [GOLD if i == 0 else ACCENT if i == 1 else GREEN if i == 2 else "#8BA3C7"
                  for i in range(len(lb))]
        fig_lb = go.Figure(go.Bar(
            x=lb["composite_score"],
            y=lb["scheme_name"].apply(lambda x: x[:28] + "…" if len(x) > 28 else x),
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        ))
        apply_theme(fig_lb, height=max(400, len(lb) * 22))
        fig_lb.update_layout(
            title="Composite Fund Score (CAGR + Sharpe + Alpha + Drawdown + Expense)",
            xaxis_title="Score (0–100)", yaxis=dict(tickfont=dict(size=9)),
        )
        st.plotly_chart(fig_lb, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — FUND FINDER (AI-STYLE RECOMMENDATION ENGINE)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖  Fund Finder":
    section_header("🤖 Fund Finder", "Tell us your goals — we'll find your perfect funds")

    st.markdown(f"""
    <div class='glass-card'>
      <div style='font-size:0.95rem;color:{TEXT_SUB};line-height:1.7;'>
        Our recommendation engine scores every tracked fund across <b style='color:{TEXT_MAIN}'>7 weighted criteria</b>
        tailored to your investment profile. The output is a personalised, ranked shortlist of the top 5 funds
        best suited to your specific goals and risk tolerance.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── User Inputs ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        goal = st.selectbox(
            "🎯 Investment Goal",
            ["Wealth Growth", "Capital Preservation", "Income Generation", "Balanced"],
            key="ff_goal"
        )
    with c2:
        risk_app = st.select_slider(
            "⚡ Risk Appetite",
            options=["Very Low", "Low", "Medium", "High", "Very High"],
            value="Medium", key="ff_risk"
        )
    with c3:
        horizon = st.selectbox(
            "🕐 Investment Horizon",
            ["< 1 Year", "1–3 Years", "3–5 Years", "5+ Years"],
            key="ff_horizon", index=2
        )

    invest_amount = st.number_input(
        "💰 Monthly SIP Amount (₹) — for projection only",
        min_value=500, max_value=500000, value=5000, step=500, key="ff_sip"
    )

    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)

    # ── Scoring Engine ────────────────────────────────────────────────────────
    # Goal → preferred category weights
    GOAL_CAT = {
        "Wealth Growth":       {"Equity": 1.0, "Hybrid": 0.5, "Debt": 0.1},
        "Capital Preservation": {"Debt": 1.0, "Hybrid": 0.6, "Equity": 0.1},
        "Income Generation":   {"Debt": 0.9, "Hybrid": 0.6, "Equity": 0.3},
        "Balanced":            {"Equity": 0.7, "Hybrid": 1.0, "Debt": 0.5},
    }
    # Risk → preferred risk grade weights
    RISK_GRADE = {
        "Very Low": {"Low": 1.0, "Moderately Low": 0.7, "Moderate": 0.3, "Moderately High": 0.1, "High": 0.0},
        "Low":      {"Low": 0.9, "Moderately Low": 1.0, "Moderate": 0.5, "Moderately High": 0.2, "High": 0.0},
        "Medium":   {"Low": 0.5, "Moderately Low": 0.7, "Moderate": 1.0, "Moderately High": 0.7, "High": 0.3},
        "High":     {"Low": 0.2, "Moderately Low": 0.4, "Moderate": 0.7, "Moderately High": 1.0, "High": 0.9},
        "Very High":{"Low": 0.0, "Moderately Low": 0.1, "Moderate": 0.3, "Moderately High": 0.7, "High": 1.0},
    }
    # Horizon → return metric weight (short-term = 1Y, long = 5Y)
    HORIZON_WT = {
        "< 1 Year":  {"return_1yr_pct": 1.0, "return_3yr_pct": 0.2, "return_5yr_pct": 0.0},
        "1–3 Years": {"return_1yr_pct": 0.5, "return_3yr_pct": 1.0, "return_5yr_pct": 0.3},
        "3–5 Years": {"return_1yr_pct": 0.2, "return_3yr_pct": 0.8, "return_5yr_pct": 1.0},
        "5+ Years":  {"return_1yr_pct": 0.1, "return_3yr_pct": 0.5, "return_5yr_pct": 1.0},
    }

    df_score = perf_df.copy()
    # Normalise continuous columns 0→1
    for col in ["return_1yr_pct","return_3yr_pct","return_5yr_pct",
                "sharpe_ratio","sortino_ratio","alpha","expense_ratio_pct","morningstar_rating"]:
        mn, mx = df_score[col].min(), df_score[col].max()
        df_score[col + "_n"] = (df_score[col] - mn) / (mx - mn + 1e-9)

    hw = HORIZON_WT[horizon]
    df_score["score_return"] = (
        hw["return_1yr_pct"] * df_score["return_1yr_pct_n"] +
        hw["return_3yr_pct"] * df_score["return_3yr_pct_n"] +
        hw["return_5yr_pct"] * df_score["return_5yr_pct_n"]
    ) / sum(hw.values())

    goal_cats = GOAL_CAT[goal]
    df_score["score_category"] = df_score["category"].apply(
        lambda c: max((v for k, v in goal_cats.items() if k.lower() in c.lower()), default=0.3)
    )

    risk_grades_map = RISK_GRADE[risk_app]
    df_score["score_risk"] = df_score["risk_grade"].apply(
        lambda r: risk_grades_map.get(r, 0.3)
    )

    df_score["score_quality"] = (
        0.4 * df_score["sharpe_ratio_n"] +
        0.3 * df_score["morningstar_rating_n"] +
        0.3 * df_score["alpha_n"]
    )

    # Expense ratio: LOWER is better → invert
    df_score["score_cost"] = 1 - df_score["expense_ratio_pct_n"]

    # Final weighted score
    df_score["final_score"] = (
        0.30 * df_score["score_return"] +
        0.25 * df_score["score_risk"] +
        0.20 * df_score["score_category"] +
        0.15 * df_score["score_quality"] +
        0.10 * df_score["score_cost"]
    ) * 100

    top5 = df_score.nlargest(5, "final_score").reset_index(drop=True)

    # ── Render Fund Cards ─────────────────────────────────────────────────────
    st.markdown(f"<div style='font-size:1.1rem;font-weight:700;margin-bottom:16px;color:{TEXT_MAIN}'>🎯 Your Top 5 Recommended Funds</div>", unsafe_allow_html=True)

    for i, row in top5.iterrows():
        score_pct = row["final_score"]
        bar_width = f"{score_pct:.0f}%"

        # Badges
        badges = ""
        if row["morningstar_rating"] >= 4: badges += f"<span class='badge badge-gold'>{stars(row['morningstar_rating'])}</span>"
        if row["sharpe_ratio"] > df_score["sharpe_ratio"].median(): badges += f"<span class='badge badge-green'>High Sharpe</span>"
        if row["expense_ratio_pct"] < df_score["expense_ratio_pct"].median(): badges += f"<span class='badge badge-teal'>Low Cost</span>"
        if row["alpha"] > 0: badges += f"<span class='badge badge-green'>+Alpha</span>"
        if row["return_3yr_pct"] > df_score["return_3yr_pct"].median(): badges += f"<span class='badge badge-teal'>Strong Returns</span>"

        medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]

        st.markdown(f"""
        <div class='fund-card'>
          <div class='fund-rank'>#{i+1}</div>
          <div style='font-size:1.2rem; margin-bottom:2px;'>{medal}</div>
          <div class='fund-name'>{row['scheme_name']}</div>
          <div class='fund-meta'>{row['fund_house']} · {row['category']} · {row['plan']}</div>
          <div>{badges}</div>
          <div style='margin-top:12px;'>
            <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
              <span style='font-size:0.78rem;color:{TEXT_SUB};'>Match Score</span>
              <span style='font-family:"JetBrains Mono",monospace;font-size:0.85rem;color:{ACCENT};font-weight:700;'>{score_pct:.1f}/100</span>
            </div>
            <div class='fund-score-bar-bg'>
              <div class='fund-score-bar' style='width:{bar_width};'></div>
            </div>
          </div>
          <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px;'>
            <div style='text-align:center;background:rgba(255,255,255,0.03);border-radius:8px;padding:8px 4px;'>
              <div style='font-size:0.72rem;color:{TEXT_SUB};'>3Y Return</div>
              <div style='font-family:"JetBrains Mono",monospace;font-size:0.95rem;color:{GREEN};font-weight:600;'>{row["return_3yr_pct"]:.2f}%</div>
            </div>
            <div style='text-align:center;background:rgba(255,255,255,0.03);border-radius:8px;padding:8px 4px;'>
              <div style='font-size:0.72rem;color:{TEXT_SUB};'>Sharpe</div>
              <div style='font-family:"JetBrains Mono",monospace;font-size:0.95rem;color:{ACCENT};font-weight:600;'>{row["sharpe_ratio"]:.2f}</div>
            </div>
            <div style='text-align:center;background:rgba(255,255,255,0.03);border-radius:8px;padding:8px 4px;'>
              <div style='font-size:0.72rem;color:{TEXT_SUB};'>Expense Ratio</div>
              <div style='font-family:"JetBrains Mono",monospace;font-size:0.95rem;color:{GOLD};font-weight:600;'>{row["expense_ratio_pct"]:.2f}%</div>
            </div>
            <div style='text-align:center;background:rgba(255,255,255,0.03);border-radius:8px;padding:8px 4px;'>
              <div style='font-size:0.72rem;color:{TEXT_SUB};'>AUM (₹ Cr)</div>
              <div style='font-family:"JetBrains Mono",monospace;font-size:0.95rem;color:{TEXT_MAIN};font-weight:600;'>₹{row["aum_crore"]:,.0f}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SIP Projection ─────────────────────────────────────────────────────────
    st.markdown("<hr class='section-sep'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1rem;font-weight:700;margin-bottom:8px;color:{TEXT_MAIN}'>📈 SIP Projection for Top Fund</div>", unsafe_allow_html=True)
    st.caption(f"Projecting monthly SIP of ₹{invest_amount:,} into '{top5.iloc[0]['scheme_name'][:35]}…' using 3Y CAGR as expected return")

    cagr    = top5.iloc[0]["return_3yr_pct"] / 100
    monthly = cagr / 12
    years_proj = {"1 Year": 12, "3 Years": 36, "5 Years": 60, "10 Years": 120}

    proj_rows = []
    for label, months in years_proj.items():
        if monthly > 0:
            fv = invest_amount * (((1 + monthly) ** months - 1) / monthly) * (1 + monthly)
        else:
            fv = invest_amount * months
        invested = invest_amount * months
        proj_rows.append({"Horizon": label, "Invested": invested, "Value": fv, "Gain": fv - invested})

    proj_df = pd.DataFrame(proj_rows)
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(name="Amount Invested", x=proj_df["Horizon"], y=proj_df["Invested"],
                               marker_color="rgba(139,163,199,0.4)"))
    fig_proj.add_trace(go.Bar(name="Expected Value", x=proj_df["Horizon"], y=proj_df["Value"],
                               marker_color=ACCENT))
    apply_theme(fig_proj, height=320)
    fig_proj.update_layout(barmode="group", title="SIP Growth Projection",
                            yaxis_title="Amount (₹)", xaxis_title="Investment Horizon")
    st.plotly_chart(fig_proj, use_container_width=True)
