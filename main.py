from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Quicklizard Marketing Dashboard",
    page_icon="🦎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------
# STYLE
# ------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: white;
}

.stApp {
    background: linear-gradient(135deg, #031b3a 0%, #0a3d7a 45%, #1259b8 100%);
}

.block-container {
    padding-top: 2rem;
    max-width: 1400px;
}

.glass-card {
    background: rgba(255,255,255,0.08);
    border-radius:20px;
    padding:1.5rem;
    margin-bottom:1rem;
}

.metric-card {
    background: rgba(255,255,255,0.07);
    border-radius:18px;
    padding:1.2rem;
}

.metric-label {
    font-size:0.9rem;
    opacity:.7;
}

.metric-value {
    font-size:2rem;
    font-weight:700;
}

.section-title{
    font-size:1.2rem;
    font-weight:600;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HELPERS
# ------------------------------------------------

def parse_month(series):
    return pd.to_datetime(series, format="%b-%y", errors="coerce")


def clean_numeric(series):
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("<", "", regex=False)
        .str.replace(">", "", regex=False)
        .str.replace("--", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def safe_div(a,b):
    if b == 0 or pd.isna(b):
        return 0
    return a/b


def fmt(v):
    if pd.isna(v):
        return "--"
    return f"{v:,.0f}"


def fmt_money(v):
    if pd.isna(v):
        return "--"
    return f"${v:,.2f}"


# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():

    kw = pd.read_csv("data/Google Paid Keywords.csv")
    geo = pd.read_csv("data/Google Paid Locations.csv")

    return kw, geo


data_loaded=True

try:
    keywords_df, geo_df = load_data()
except:
    data_loaded=False


# ------------------------------------------------
# CLEAN DATA
# ------------------------------------------------

if data_loaded:

    keywords_df["Month_dt"] = parse_month(keywords_df["Month"])
    keywords_df["Keyword"] = keywords_df["Keyword"].astype(str).str.strip()

    numeric_cols = [
        "Cost","Clicks","Impressions","Conversions",
        "Avg. CPC","Max. CPC","Cost / conv.","Interactions"
    ]

    for c in numeric_cols:
        if c in keywords_df.columns:
            keywords_df[c]=clean_numeric(keywords_df[c])

    enabled_keywords = keywords_df[
        keywords_df["Keyword status"].str.lower()=="enabled"
    ]

    geo_df["Month_dt"]=parse_month(geo_df["Month"])

    geo_numeric = [
        "Cost","Conversions","Interactions","Impr."
    ]

    for c in geo_numeric:
        if c in geo_df.columns:
            geo_df[c]=clean_numeric(geo_df[c])

    months=sorted(
        pd.concat([enabled_keywords["Month_dt"],geo_df["Month_dt"]]).dropna().unique()
    )

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown("""
<div class="glass-card">
<h1>🦎 Quicklizard Marketing Dashboard</h1>
<p>Q4-Q1 2026 Marketing Overview for our 3 main channels:
Google Paid Keywords, Google Organic and Linkedin Campaigns</p>
</div>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4=st.tabs(
    ["Overview","Google Paid Keywords","Google Organic","LinkedIn Campaigns"]
)

# ------------------------------------------------
# GOOGLE PAID TAB
# ------------------------------------------------

with tab2:

    if not data_loaded:
        st.error("CSV files not found in /data folder.")
        st.stop()

    st.markdown('<div class="section-title">Filters</div>',unsafe_allow_html=True)

    c1,c2=st.columns(2)

    with c1:

        labels=[m.strftime("%b %Y") for m in months]

        idx=st.select_slider(
            "Date Range",
            options=list(range(len(labels))),
            value=(0,len(labels)-1),
            format_func=lambda x:labels[x]
        )

        start=months[idx[0]]
        end=months[idx[1]]

    with c2:

        countries=sorted(geo_df["Location"].dropna().unique())
        selected=st.multiselect("Countries",countries,default=countries)

    # filters
    kw=enabled_keywords[
        (enabled_keywords["Month_dt"]>=start) &
        (enabled_keywords["Month_dt"]<=end)
    ]

    geo=geo_df[
        (geo_df["Month_dt"]>=start) &
        (geo_df["Month_dt"]<=end)
    ]

    geo=geo[geo["Location"].isin(selected)]

    # ------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------

    spend=kw["Cost"].sum()
    conv=kw["Conversions"].sum()
    clicks=kw["Clicks"].sum()
    cpa=safe_div(spend,conv)

    k1,k2,k3,k4=st.columns(4)

    k1.markdown(f"""
<div class="metric-card">
<div class="metric-label">Total Spend</div>
<div class="metric-value">{fmt_money(spend)}</div>
</div>
""",unsafe_allow_html=True)

    k2.markdown(f"""
<div class="metric-card">
<div class="metric-label">Total Conversions</div>
<div class="metric-value">{fmt(conv)}</div>
</div>
""",unsafe_allow_html=True)

    k3.markdown(f"""
<div class="metric-card">
<div class="metric-label">Avg CPA</div>
<div class="metric-value">{fmt_money(cpa)}</div>
</div>
""",unsafe_allow_html=True)

    k4.markdown(f"""
<div class="metric-card">
<div class="metric-label">Total Clicks</div>
<div class="metric-value">{fmt(clicks)}</div>
</div>
""",unsafe_allow_html=True)

    st.divider()

    # ------------------------------------------------
    # KEYWORD SECTION
    # ------------------------------------------------

    st.subheader("Top Performing Keywords")

    trend=kw.groupby("Month_dt")[["Clicks","Conversions","Cost"]].sum()
    st.line_chart(trend)

    kw_table=kw.groupby("Keyword")[["Cost","Conversions","Clicks","Impressions"]].sum()

    kw_table["CTR %"]=kw_table["Clicks"]/kw_table["Impressions"]*100
    kw_table["CPA"]=kw_table["Cost"]/kw_table["Conversions"]

    st.write("Top Keywords by Conversions")

    st.dataframe(
        kw_table.sort_values("Conversions",ascending=False)
        .head(10)
    )

    st.write("Top Keywords by Spend")

    st.dataframe(
        kw_table.sort_values("Cost",ascending=False)
        .head(10)
    )

    st.divider()

    # ------------------------------------------------
    # GEO SECTION
    # ------------------------------------------------

    st.subheader("GEO Performance")

    geo_trend=geo.groupby("Month_dt")[["Cost","Conversions","Interactions"]].sum()

    st.line_chart(geo_trend)

    geo_table=geo.groupby("Location")[["Cost","Conversions","Interactions","Impr."]].sum()

    geo_table["CPA"]=geo_table["Cost"]/geo_table["Conversions"]

    st.write("Top Countries by Conversions")

    st.dataframe(
        geo_table.sort_values("Conversions",ascending=False)
        .head(10)
    )

    st.write("Top Countries by Spend")

    st.dataframe(
        geo_table.sort_values("Cost",ascending=False)
        .head(10)
    )
