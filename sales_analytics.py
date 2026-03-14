import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
 
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
 
h1, h2, h3, .metric-label {
    font-family: 'Syne', sans-serif !important;
}
 
/* Main background */
.stApp {
    background: #0b0f1a;
    color: #e8eaf0;
}
 
/* Sidebar */
[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1f2937;
}
 
[data-testid="stSidebar"] * {
    color: #d1d5db !important;
}
 
/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #151d2e 0%, #1a2340 100%);
    border: 1px solid #1f3460;
    border-radius: 16px;
    padding: 24px 28px;
    position: relative;
    overflow: hidden;
}
 
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
}
 
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1;
    margin: 8px 0 4px;
}
 
.kpi-label {
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
}
 
.kpi-delta {
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 6px;
}
 
.kpi-delta.up   { color: #34d399; }
.kpi-delta.down { color: #f87171; }
 
/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 16px;
}
 
/* Plotly chart containers */
.chart-container {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 20px;
}
 
/* DataFrame table */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
 
/* Divider */
hr { border-color: #1f2937; }
</style>
""", unsafe_allow_html=True)
 
# ── Sample Data Generation ────────────────────────────────────────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    random.seed(42)
 
    regions    = ["North", "South", "East", "West"]
    categories = ["Software", "Hardware", "Services", "Consulting"]
    reps       = ["Alice Chen", "Bob Martinez", "Carol Singh", "David Kim",
                  "Eva Patel", "Frank Lee", "Grace Wu", "Henry Brown"]
 
    start = datetime(2023, 1, 1)
    rows  = []
    for i in range(600):
        d = start + timedelta(days=random.randint(0, 364))
        base  = random.uniform(2000, 25000)
        trend = (d.month / 12) * 0.3
        rows.append({
            "Date":     d,
            "Region":   random.choice(regions),
            "Category": random.choice(categories),
            "Rep":      random.choice(reps),
            "Revenue":  round(base * (1 + trend + np.random.normal(0, 0.1)), 2),
            "Units":    random.randint(1, 80),
            "Discount": round(random.uniform(0, 0.25), 2),
        })
 
    df = pd.DataFrame(rows)
    df["Profit"] = (df["Revenue"] * (1 - df["Discount"]) * 0.38).round(2)
    df["Month"]  = df["Date"].dt.to_period("M").astype(str)
    df["Quarter"]= df["Date"].dt.to_period("Q").astype(str)
    return df
 
df_all = generate_data()
 
# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛 Filters")
    st.markdown("---")
 
    min_date = df_all["Date"].min().date()
    max_date = df_all["Date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
 
    st.markdown("---")
    regions_sel = st.multiselect(
        "Region",
        options=sorted(df_all["Region"].unique()),
        default=sorted(df_all["Region"].unique()),
    )
 
    cats_sel = st.multiselect(
        "Category",
        options=sorted(df_all["Category"].unique()),
        default=sorted(df_all["Category"].unique()),
    )
 
    reps_sel = st.multiselect(
        "Sales Rep",
        options=sorted(df_all["Rep"].unique()),
        default=sorted(df_all["Rep"].unique()),
    )
 
    st.markdown("---")
    granularity = st.radio("Chart Granularity", ["Monthly", "Quarterly"], index=0)
 
# ── Filter Data ───────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date
 
df = df_all[
    (df_all["Date"].dt.date >= start_d) &
    (df_all["Date"].dt.date <= end_d) &
    (df_all["Region"].isin(regions_sel)) &
    (df_all["Category"].isin(cats_sel)) &
    (df_all["Rep"].isin(reps_sel))
].copy()
 
# Prior period for delta
period_days    = max((end_d - start_d).days, 1)
prior_start    = start_d - timedelta(days=period_days)
prior_end      = start_d - timedelta(days=1)
df_prior = df_all[
    (df_all["Date"].dt.date >= prior_start) &
    (df_all["Date"].dt.date <= prior_end) &
    (df_all["Region"].isin(regions_sel)) &
    (df_all["Category"].isin(cats_sel)) &
    (df_all["Rep"].isin(reps_sel))
]
 
def delta_pct(curr, prev):
    if prev == 0:
        return 0
    return ((curr - prev) / prev) * 100
 
# ── Metrics ───────────────────────────────────────────────────────────────────
total_rev    = df["Revenue"].sum()
total_profit = df["Profit"].sum()
total_units  = df["Units"].sum()
avg_deal     = df["Revenue"].mean() if len(df) else 0
 
prev_rev    = df_prior["Revenue"].sum()
prev_profit = df_prior["Profit"].sum()
prev_units  = df_prior["Units"].sum()
prev_deal   = df_prior["Revenue"].mean() if len(df_prior) else 0
 
# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-family:Syne;font-size:2.4rem;font-weight:800;
           color:#f1f5f9;margin-bottom:0;letter-spacing:-0.02em;'>
  Sales Analytics
</h1>
<p style='color:#475569;font-size:1rem;margin-top:4px;'>
  Revenue · Profit · Performance Dashboard
</p>
""", unsafe_allow_html=True)
st.markdown("---")
 
# ── KPI Cards ─────────────────────────────────────────────────────────────────
accents = ["#6366f1", "#f59e0b", "#10b981", "#ec4899"]
labels  = ["Total Revenue", "Gross Profit", "Units Sold", "Avg Deal Size"]
values  = [f"${total_rev:,.0f}", f"${total_profit:,.0f}",
           f"{total_units:,}", f"${avg_deal:,.0f}"]
deltas  = [
    delta_pct(total_rev,    prev_rev),
    delta_pct(total_profit, prev_profit),
    delta_pct(total_units,  prev_units),
    delta_pct(avg_deal,     prev_deal),
]
 
cols = st.columns(4)
for i, col in enumerate(cols):
    d    = deltas[i]
    dcls = "up" if d >= 0 else "down"
    darr = "▲" if d >= 0 else "▼"
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="--accent:{accents[i]}">
            <div class="kpi-label">{labels[i]}</div>
            <div class="kpi-value">{values[i]}</div>
            <div class="kpi-delta {dcls}">{darr} {abs(d):.1f}% vs prior period</div>
        </div>
        """, unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── Charts Row 1 ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])
 
COLORS = ["#6366f1", "#f59e0b", "#10b981", "#ec4899",
          "#38bdf8", "#a78bfa", "#fb923c", "#34d399"]
 
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="DM Sans"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    xaxis=dict(gridcolor="#1f2937", linecolor="#1f2937"),
    yaxis=dict(gridcolor="#1f2937", linecolor="#1f2937"),
)
 
with col1:
    st.markdown("<div class='section-title'>Revenue & Profit Over Time</div>",
                unsafe_allow_html=True)
    grp_col = "Month" if granularity == "Monthly" else "Quarter"
    ts = (df.groupby(grp_col)[["Revenue", "Profit"]]
            .sum().reset_index()
            .sort_values(grp_col))
 
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ts[grp_col], y=ts["Revenue"], name="Revenue",
        marker_color="#6366f1", opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=ts[grp_col], y=ts["Profit"], name="Profit",
        marker_color="#10b981", opacity=0.85,
    ))
    fig.update_layout(**CHART_LAYOUT, barmode="group",
                      title=dict(text="", x=0.0),
                      height=320)
    st.plotly_chart(fig, use_container_width=True)
 
with col2:
    st.markdown("<div class='section-title'>Revenue by Category</div>",
                unsafe_allow_html=True)
    cat_data = df.groupby("Category")["Revenue"].sum().reset_index()
    fig2 = px.pie(
        cat_data, names="Category", values="Revenue",
        hole=0.55,
        color_discrete_sequence=COLORS,
    )
    fig2.update_traces(textfont_color="#e8eaf0",
                       marker=dict(line=dict(color="#0b0f1a", width=2)))
    pie_layout = {**CHART_LAYOUT, "height": 320}
    pie_layout["legend"] = dict(orientation="h", yanchor="bottom",
                                y=-0.25, x=0.5, xanchor="center",
                                font=dict(color="#94a3b8"))
    fig2.update_layout(**pie_layout)
    st.plotly_chart(fig2, use_container_width=True)
 
# ── Charts Row 2 ──────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)
 
with col3:
    st.markdown("<div class='section-title'>Revenue by Region</div>",
                unsafe_allow_html=True)
    reg_data = df.groupby("Region")["Revenue"].sum().reset_index().sort_values("Revenue")
    fig3 = px.bar(
        reg_data, x="Revenue", y="Region", orientation="h",
        color="Region", color_discrete_sequence=COLORS,
    )
    fig3.update_layout(**CHART_LAYOUT, height=300, showlegend=False)
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True)
 
with col4:
    st.markdown("<div class='section-title'>Top Sales Reps</div>",
                unsafe_allow_html=True)
    rep_data = (df.groupby("Rep")["Revenue"].sum()
                  .reset_index()
                  .sort_values("Revenue", ascending=False)
                  .head(8))
    fig4 = px.bar(
        rep_data, x="Rep", y="Revenue",
        color="Revenue",
        color_continuous_scale=["#1f2d52", "#6366f1"],
    )
    fig4.update_layout(**CHART_LAYOUT, height=300,
                       coloraxis_showscale=False)
    fig4.update_traces(marker_line_width=0)
    fig4.update_xaxes(tickangle=-30)
    st.plotly_chart(fig4, use_container_width=True)
 
# ── Scatter ───────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Revenue vs Discount Rate</div>",
            unsafe_allow_html=True)
fig5 = px.scatter(
    df, x="Discount", y="Revenue",
    color="Category", size="Units",
    color_discrete_sequence=COLORS,
    opacity=0.7,
    trendline="ols",
)
fig5.update_layout(**CHART_LAYOUT, height=320)
st.plotly_chart(fig5, use_container_width=True)
 
# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-title'>Transaction Data</div>",
            unsafe_allow_html=True)
 
search = st.text_input("🔍  Search by Rep or Region", "")
 
display_df = df[["Date", "Region", "Category", "Rep",
                 "Revenue", "Profit", "Units", "Discount"]].copy()
display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
display_df["Revenue"]  = display_df["Revenue"].map("${:,.2f}".format)
display_df["Profit"]   = display_df["Profit"].map("${:,.2f}".format)
display_df["Discount"] = display_df["Discount"].map("{:.0%}".format)
 
if search:
    mask = (
        display_df["Rep"].str.contains(search, case=False) |
        display_df["Region"].str.contains(search, case=False)
    )
    display_df = display_df[mask]
 
st.dataframe(
    display_df.sort_values("Date", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=380,
)
 
st.markdown(f"<p style='color:#475569;font-size:0.8rem;margin-top:8px;'>"
            f"Showing {len(display_df):,} of {len(df):,} transactions</p>",
            unsafe_allow_html=True)
