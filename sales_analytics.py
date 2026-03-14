import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #F8F9FC !important;
    color: #1A202C;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
    color: #4A5568 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #1A202C !important;
    font-family: 'Manrope', sans-serif !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 22px 24px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    transition: box-shadow 0.2s ease;
}
.kpi-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
    border-radius: 0 0 12px 12px;
}
.kpi-icon {
    font-size: 1.3rem;
    margin-bottom: 10px;
    display: block;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #718096;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Manrope', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #1A202C;
    line-height: 1.1;
    margin-bottom: 8px;
}
.kpi-delta {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 20px;
}
.kpi-delta.up   { color: #276749; background: #C6F6D5; }
.kpi-delta.down { color: #9B2C2C; background: #FED7D7; }

/* ── Section titles ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
    margin-top: 4px;
}
.section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #2D3748;
}
.section-line {
    flex: 1;
    height: 1px;
    background: #E2E8F0;
}

/* ── Page header ── */
.page-header {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.page-title {
    font-family: 'Manrope', sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
    color: #1A202C;
    letter-spacing: -0.03em;
    margin: 0;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #718096;
    margin: 2px 0 0;
    font-weight: 400;
}
.page-badge {
    background: #EBF4FF;
    color: #2B6CB0;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: 20px;
    border: 1px solid #BEE3F8;
    letter-spacing: 0.03em;
}

/* ── Misc ── */
hr { border: none; border-top: 1px solid #E2E8F0; margin: 20px 0; }

[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
    font-size: 0.85rem !important;
    color: #2D3748 !important;
    background: #FFFFFF !important;
}
[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid #E2E8F0 !important;
    overflow: hidden;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
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
        d     = start + timedelta(days=random.randint(0, 364))
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
    df["Profit"]  = (df["Revenue"] * (1 - df["Discount"]) * 0.38).round(2)
    df["Month"]   = df["Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Date"].dt.to_period("Q").astype(str)
    return df

df_all = generate_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:12px 4px 20px;border-bottom:1px solid #E2E8F0;margin-bottom:20px;'>
        <div style='font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:800;
                    color:#1A202C;letter-spacing:-0.02em;'>⚡ Sales Intelligence</div>
        <div style='font-size:0.75rem;color:#A0AEC0;margin-top:2px;'>Filter &amp; Explore</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📅 Date Range**")
    min_date = df_all["Date"].min().date()
    max_date = df_all["Date"].max().date()
    date_range = st.date_input(
        "", value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
        label_visibility="collapsed",
    )
    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

    st.markdown("**🌍 Region**")
    regions_sel = st.multiselect("", options=sorted(df_all["Region"].unique()),
                                 default=sorted(df_all["Region"].unique()),
                                 label_visibility="collapsed")

    st.markdown("**📦 Category**")
    cats_sel = st.multiselect("", options=sorted(df_all["Category"].unique()),
                               default=sorted(df_all["Category"].unique()),
                               label_visibility="collapsed")

    st.markdown("**👤 Sales Rep**")
    reps_sel = st.multiselect("", options=sorted(df_all["Rep"].unique()),
                               default=sorted(df_all["Rep"].unique()),
                               label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📐 Granularity**")
    granularity = st.radio("", ["Monthly", "Quarterly"], index=0,
                           label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.72rem;color:#A0AEC0;text-align:center;padding:4px 0;'>"
        "Sales Analytics v2.0 · 2023</div>",
        unsafe_allow_html=True,
    )

# ── Filter ────────────────────────────────────────────────────────────────────
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

period_days = max((end_d - start_d).days, 1)
prior_start = start_d - timedelta(days=period_days)
prior_end   = start_d - timedelta(days=1)
df_prior = df_all[
    (df_all["Date"].dt.date >= prior_start) &
    (df_all["Date"].dt.date <= prior_end) &
    (df_all["Region"].isin(regions_sel)) &
    (df_all["Category"].isin(cats_sel)) &
    (df_all["Rep"].isin(reps_sel))
]

def delta_pct(curr, prev):
    return 0 if prev == 0 else ((curr - prev) / prev) * 100

total_rev    = df["Revenue"].sum()
total_profit = df["Profit"].sum()
total_units  = int(df["Units"].sum())
avg_deal     = df["Revenue"].mean() if len(df) else 0

prev_rev    = df_prior["Revenue"].sum()
prev_profit = df_prior["Profit"].sum()
prev_units  = df_prior["Units"].sum()
prev_deal   = df_prior["Revenue"].mean() if len(df_prior) else 0

# ── Chart theme ───────────────────────────────────────────────────────────────
COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444",
          "#8B5CF6", "#06B6D4", "#F97316", "#84CC16"]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#4A5568", family="Inter, sans-serif", size=12),
    margin=dict(l=8, r=8, t=10, b=8),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#4A5568", size=11),
        borderwidth=0,
    ),
    xaxis=dict(
        gridcolor="#F0F4F8", linecolor="#E2E8F0",
        tickfont=dict(color="#718096", size=11), zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#F0F4F8", linecolor="#E2E8F0",
        tickfont=dict(color="#718096", size=11), zeroline=False,
    ),
)

def section(title):
    st.markdown(
        f"<div class='section-header'>"
        f"<span class='section-title'>{title}</span>"
        f"<span class='section-line'></span>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div>
        <div class="page-title">Sales Performance Dashboard</div>
        <div class="page-subtitle">Revenue · Profit · Pipeline · Rep Analytics</div>
    </div>
    <span class="page-badge">📅 {start_d.strftime("%b %d")} — {end_d.strftime("%b %d, %Y")}</span>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
kpis = [
    ("💰", "Total Revenue",  f"${total_rev:,.0f}",    delta_pct(total_rev,    prev_rev),    "#3B82F6"),
    ("📈", "Gross Profit",   f"${total_profit:,.0f}", delta_pct(total_profit, prev_profit), "#10B981"),
    ("📦", "Units Sold",     f"{total_units:,}",      delta_pct(total_units,  prev_units),  "#F59E0B"),
    ("🤝", "Avg Deal Size",  f"${avg_deal:,.0f}",     delta_pct(avg_deal,     prev_deal),   "#8B5CF6"),
]

cols = st.columns(4)
for col, (icon, label, value, d, accent) in zip(cols, kpis):
    dcls = "up" if d >= 0 else "down"
    darr = "▲" if d >= 0 else "▼"
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="--accent:{accent}">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <span class="kpi-delta {dcls}">{darr} {abs(d):.1f}% vs prior period</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Row 1: Time Series + Donut ────────────────────────────────────────────────
col1, col2 = st.columns([3, 2], gap="medium")

with col1:
    section("Revenue & Profit Over Time")
    grp_col = "Month" if granularity == "Monthly" else "Quarter"
    ts = (df.groupby(grp_col)[["Revenue", "Profit"]]
            .sum().reset_index().sort_values(grp_col))
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=ts[grp_col], y=ts["Revenue"], name="Revenue",
        marker_color="#3B82F6", marker_line_width=0, opacity=0.9,
    ))
    fig1.add_trace(go.Bar(
        x=ts[grp_col], y=ts["Profit"], name="Profit",
        marker_color="#10B981", marker_line_width=0, opacity=0.9,
    ))
    fig1.update_layout(**CHART_LAYOUT, barmode="group", height=310,
                       bargap=0.25, bargroupgap=0.08)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    section("Revenue by Category")
    cat_data = df.groupby("Category")["Revenue"].sum().reset_index()
    fig2 = px.pie(cat_data, names="Category", values="Revenue",
                  hole=0.60, color_discrete_sequence=COLORS)
    fig2.update_traces(
        textfont=dict(color="#2D3748", size=11, family="Inter"),
        marker=dict(line=dict(color="#F8F9FC", width=3)),
        pull=[0.03] * len(cat_data),
    )
    pie_layout = {**CHART_LAYOUT, "height": 310}
    pie_layout["legend"] = dict(
        orientation="h", yanchor="bottom", y=-0.28,
        x=0.5, xanchor="center",
        font=dict(color="#4A5568", size=11), bgcolor="rgba(0,0,0,0)",
    )
    fig2.update_layout(**pie_layout)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Region + Reps ──────────────────────────────────────────────────────
col3, col4 = st.columns(2, gap="medium")

with col3:
    section("Revenue by Region")
    reg_data = (df.groupby("Region")["Revenue"].sum()
                  .reset_index().sort_values("Revenue"))
    fig3 = px.bar(
        reg_data, x="Revenue", y="Region", orientation="h",
        color="Region", color_discrete_sequence=COLORS,
        text=reg_data["Revenue"].map("${:,.0f}".format),
    )
    fig3.update_traces(marker_line_width=0,
                       textfont=dict(color="#4A5568", size=11),
                       textposition="outside")
    _l3 = {**CHART_LAYOUT, "height": 290, "showlegend": False}
    _l3["xaxis"] = dict(visible=False)
    fig3.update_layout(**_l3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    section("Top Sales Representatives")
    rep_data = (df.groupby("Rep")["Revenue"].sum()
                  .reset_index()
                  .sort_values("Revenue", ascending=False)
                  .head(8))
    fig4 = px.bar(
        rep_data, x="Revenue", y="Rep", orientation="h",
        color="Revenue",
        color_continuous_scale=["#DBEAFE", "#1D4ED8"],
        text=rep_data["Revenue"].map("${:,.0f}".format),
    )
    fig4.update_traces(marker_line_width=0,
                       textfont=dict(color="#4A5568", size=11),
                       textposition="outside")
    _l4 = {**CHART_LAYOUT, "height": 290, "coloraxis_showscale": False}
    _l4["xaxis"] = dict(visible=False)
    _l4["yaxis"] = dict(gridcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)",
                        tickfont=dict(color="#2D3748", size=11))
    fig4.update_layout(**_l4)
    st.plotly_chart(fig4, use_container_width=True)

# ── Scatter ───────────────────────────────────────────────────────────────────
section("Revenue vs Discount Rate — Correlation Analysis")
fig5 = px.scatter(
    df, x="Discount", y="Revenue",
    color="Category", size="Units",
    color_discrete_sequence=COLORS,
    opacity=0.65, trendline="ols",
    hover_data=["Rep", "Region"],
)
fig5.update_traces(marker=dict(line=dict(width=0.5, color="#FFFFFF")))
_l5 = {**CHART_LAYOUT, "height": 320}
_l5["xaxis"] = dict(tickformat=".0%", gridcolor="#F0F4F8",
                    title=dict(text="Discount Rate", font=dict(color="#718096", size=12)))
_l5["yaxis"] = dict(tickprefix="$", gridcolor="#F0F4F8",
                    title=dict(text="Revenue", font=dict(color="#718096", size=12)))
fig5.update_layout(**_l5)
st.plotly_chart(fig5, use_container_width=True)

# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
tcol1, tcol2 = st.columns([3, 1], gap="medium")
with tcol1:
    section("Transaction Records")
with tcol2:
    search = st.text_input("", placeholder="🔍  Search rep or region…",
                           label_visibility="collapsed")

display_df = df[["Date", "Region", "Category", "Rep",
                 "Revenue", "Profit", "Units", "Discount"]].copy()
display_df["Date"]     = display_df["Date"].dt.strftime("%b %d, %Y")
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
    use_container_width=True, height=380,
)
st.markdown(
    f"<p style='color:#A0AEC0;font-size:0.76rem;margin-top:6px;'>"
    f"Showing <strong style='color:#4A5568'>{len(display_df):,}</strong> of "
    f"<strong style='color:#4A5568'>{len(df):,}</strong> transactions</p>",
    unsafe_allow_html=True,
)
