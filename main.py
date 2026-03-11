from pathlib import Path
import calendar
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
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1450px;
}

h1, h2, h3, h4, h5, h6, p, li, label, div, span {
    color: white !important;
}

.glass-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 20px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 1.1rem;
    min-height: 125px;
}

.metric-label {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.72) !important;
    margin-bottom: 0.45rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    color: white !important;
}

.metric-delta {
    font-size: 0.92rem;
    color: rgba(255,255,255,0.80) !important;
    margin-top: 0.35rem;
}

.section-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.65rem;
    color: white !important;
}

.small-note {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.72) !important;
}

.insight-box {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.8rem;
}

.insight-title {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
    color: white !important;
}

.insight-text {
    font-size: 0.95rem;
    line-height: 1.55;
    color: rgba(255,255,255,0.86) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px 18px;
    color: white !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(255,255,255,0.18) !important;
    color: white !important;
}

div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
}

.stMultiSelect div[data-baseweb="tag"] {
    background-color: rgba(255,255,255,0.18) !important;
    border-radius: 10px !important;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 0.25rem;
}

hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.15);
    margin-top: 1.6rem;
    margin-bottom: 1.6rem;
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
        .str.replace("#DIV/0!", "", regex=False)
        .str.replace("--", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def safe_div(a, b):
    if b == 0 or pd.isna(b):
        return 0
    return a / b


def fmt_number(v):
    if pd.isna(v):
        return "--"
    return f"{round(v):,}"


def fmt_money(v):
    if pd.isna(v):
        return "--"
    return f"${round(v):,}"


def fmt_pct(v):
    if pd.isna(v):
        return "--"
    return f"{round(v)}%"


def is_valid_country(location_value: str) -> bool:
    if pd.isna(location_value):
        return False

    value = str(location_value).strip()

    if value == "":
        return False

    if value.startswith("Total:"):
        return False

    if "," in value:
        return False

    invalid_values = {
        "Unknown",
        "Other locations",
        "Presence or interest",
        "Search",
        "Display",
        "Performance Max",
        "Account",
        "Locations",
    }
    if value in invalid_values:
        return False

    return True


def build_campaign_rows(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df = df.iloc[:, :13]
    df.columns = [f"col_{i}" for i in range(df.shape[1])]

    month_map = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
    month_map.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})

    rows = []
    current_month_name = None
    current_year = 2025
    last_month_num = None

    for _, row in df.iterrows():
        c0 = str(row["col_0"]).strip() if pd.notna(row["col_0"]) else ""
        c1 = str(row["col_1"]).strip() if pd.notna(row["col_1"]) else ""

        if c0:
            month_token = c0.split()[0].strip().lower()
            if month_token in month_map:
                month_num = month_map[month_token]
                if last_month_num is not None and month_num < last_month_num:
                    current_year += 1
                last_month_num = month_num
                current_month_name = calendar.month_abbr[month_num]

        if c1 == "Campaign":
            continue

        if c1 == "" or c1.lower() == "nan":
            continue

        if c1 == "Total":
            continue

        if current_month_name is None:
            continue

        month_str = f"{current_month_name}-{str(current_year)[-2:]}"

        rows.append(
            {
                "Month": month_str,
                "Campaign": c1,
                "Cost": row["col_2"],
                "Impr.": row["col_3"],
                "Clicks": row["col_4"],
                "CTR": row["col_5"],
                "Avg. CPC": row["col_6"],
                "HS leads": row["col_7"],
                "CPL": row["col_8"],
                "SAL": row["col_9"],
                "Open deal": row["col_10"],
                "Cost per SAL": row["col_11"],
            }
        )

    return pd.DataFrame(rows)


def build_paid_analysis(campaign_df: pd.DataFrame, keyword_df: pd.DataFrame) -> dict:
    if campaign_df.empty and keyword_df.empty:
        return {
            "summary": "No paid search data is available for the selected filters.",
            "efficiency": "There is not enough data to identify efficiency gaps.",
            "opportunity": "There is not enough data to identify growth opportunities.",
        }

    summary_parts = []
    efficiency_parts = []
    opportunity_parts = []

    if not campaign_df.empty:
        total_spend = campaign_df["Cost"].sum()
        total_clicks = campaign_df["Clicks"].sum()
        total_hs_leads = campaign_df["HS leads"].sum()
        total_sal = campaign_df["SAL"].sum()
        total_open_deals = campaign_df["Open deal"].sum()
        overall_ctr = safe_div(total_clicks, campaign_df["Impr."].sum()) * 100
        cpl = safe_div(total_spend, total_hs_leads)

        campaign_rank = campaign_df.groupby("Campaign", as_index=False)[
            ["Cost", "Clicks", "Impr.", "HS leads", "SAL", "Open deal"]
        ].sum()
        campaign_rank["CTR %"] = campaign_rank.apply(
            lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1
        )
        campaign_rank["CPL"] = campaign_rank.apply(
            lambda r: safe_div(r["Cost"], r["HS leads"]), axis=1
        )
        campaign_rank["Cost per SAL"] = campaign_rank.apply(
            lambda r: safe_div(r["Cost"], r["SAL"]), axis=1
        )

        top_lead_campaign = campaign_rank.sort_values(
            ["HS leads", "SAL", "Open deal"], ascending=[False, False, False]
        ).head(1)

        if not top_lead_campaign.empty:
            top_campaign_name = top_lead_campaign.iloc[0]["Campaign"]
            top_campaign_leads = top_lead_campaign.iloc[0]["HS leads"]
            summary_parts.append(
                f"Across the selected view, Google Paid generated {fmt_money(total_spend)} in spend, "
                f"{fmt_number(total_clicks)} clicks, {fmt_number(total_hs_leads)} HS leads, "
                f"{fmt_number(total_sal)} SALs, and {fmt_number(total_open_deals)} open deals. "
                f"Overall CTR is {fmt_pct(overall_ctr)} and blended CPL is {fmt_money(cpl)}. "
                f"The strongest campaign by lead generation is {top_campaign_name} with {fmt_number(top_campaign_leads)} HS leads."
            )

        inefficient_campaigns = campaign_rank[
            (campaign_rank["Cost"] > campaign_rank["Cost"].median()) &
            (campaign_rank["HS leads"] <= campaign_rank["HS leads"].median())
        ].sort_values("Cost", ascending=False)

        if not inefficient_campaigns.empty:
            weak_names = inefficient_campaigns["Campaign"].head(3).tolist()
            efficiency_parts.append(
                f"The clearest efficiency gap is in higher-spend campaigns that are not producing enough downstream outcomes. "
                f"The main watchlist campaigns are {', '.join(weak_names)}. These likely need tighter audience intent, ad group pruning, "
                f"and stronger landing page relevance."
            )

        pipeline_gap_campaigns = campaign_rank[
            (campaign_rank["HS leads"] > 0) &
            (campaign_rank["Open deal"] == 0)
        ].sort_values(["HS leads", "SAL"], ascending=[False, False])

        if not pipeline_gap_campaigns.empty:
            gap_names = pipeline_gap_campaigns["Campaign"].head(3).tolist()
            opportunity_parts.append(
                f"There is a clear lead-to-pipeline gap in campaigns that are generating engagement or leads without enough downstream deal creation. "
                f"The top examples are {', '.join(gap_names)}. These campaigns are strong candidates for offer testing, qualification review, "
                f"and tighter handoff into sales."
            )

    if not keyword_df.empty:
        keyword_rollup = keyword_df.groupby("Keyword", as_index=False)[
            ["Cost", "Clicks", "Impressions", "Conversions"]
        ].sum()
        keyword_rollup["CTR %"] = keyword_rollup.apply(
            lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1
        )
        keyword_rollup["Cost / Conv."] = keyword_rollup.apply(
            lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1
        )

        high_spend_low_conv = keyword_rollup[
            (keyword_rollup["Cost"] > keyword_rollup["Cost"].median()) &
            (keyword_rollup["Conversions"] <= keyword_rollup["Conversions"].median())
        ].sort_values("Cost", ascending=False)

        if not high_spend_low_conv.empty:
            kw_names = high_spend_low_conv["Keyword"].head(3).tolist()
            efficiency_parts.append(
                f"At the keyword level, the weakest efficiency is concentrated in {', '.join(kw_names)}. "
                f"These terms are consuming budget without converting strongly enough and should be reviewed for match type control, "
                f"search term pruning, and bid adjustments."
            )

        high_impr_low_ctr = keyword_rollup[
            (keyword_rollup["Impressions"] > keyword_rollup["Impressions"].median()) &
            (keyword_rollup["CTR %"] < keyword_rollup["CTR %"].median())
        ].sort_values("Impressions", ascending=False)

        if not high_impr_low_ctr.empty:
            kw_opp_names = high_impr_low_ctr["Keyword"].head(3).tolist()
            opportunity_parts.append(
                f"One missed opportunity is in keywords with meaningful visibility but weak click-through rates, especially {', '.join(kw_opp_names)}. "
                f"These are good candidates for message refinement, stronger ad copy, and more specific intent segmentation."
            )

    if not summary_parts:
        summary_parts.append("Paid performance data is available, but there is not enough clean detail to summarize it confidently.")

    if not efficiency_parts:
        efficiency_parts.append("No major efficiency outlier stands out in the selected slice, which suggests spend is relatively concentrated and controlled.")

    if not opportunity_parts:
        opportunity_parts.append("No obvious missed opportunity dominates the current view. The next lever may be scaling what is already converting efficiently.")

    return {
        "summary": " ".join(summary_parts),
        "efficiency": " ".join(efficiency_parts),
        "opportunity": " ".join(opportunity_parts),
    }


def percentage_columns(df: pd.DataFrame):
    pct_cols = []
    for col in df.columns:
        lower = col.lower()
        if "%" in col or "ctr" in lower or "rate" in lower:
            pct_cols.append(col)
    return pct_cols


def currency_columns(df: pd.DataFrame):
    money_cols = []
    for col in df.columns:
        lower = col.lower()
        if "cost" in lower or "cpc" in lower or "cpl" in lower or "cpa" in lower:
            money_cols.append(col)
    return money_cols


def style_dataframe(df: pd.DataFrame):
    pct_cols = percentage_columns(df)
    money_cols = currency_columns(df)
    int_cols = [c for c in df.columns if c not in pct_cols and c not in money_cols and c != "Keyword" and c != "Campaign" and c != "Country"]

    format_map = {}
    for c in pct_cols:
        format_map[c] = lambda x: "--" if pd.isna(x) else f"{round(x)}%"
    for c in money_cols:
        format_map[c] = lambda x: "--" if pd.isna(x) else f"${round(x):,}"
    for c in int_cols:
        format_map[c] = lambda x: "--" if pd.isna(x) else f"{round(x):,}"

    return df.style.format(format_map)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():
    keywords_path = Path("data/Google Paid Keywords.csv")
    locations_path = Path("data/Google Paid Locations.csv")
    campaigns_path = Path("data/Google Paid Campaigns.csv")

    keywords_df = pd.read_csv(keywords_path)
    geo_df = pd.read_csv(locations_path)
    campaign_raw_df = pd.read_csv(campaigns_path, header=None)

    return keywords_df, geo_df, campaign_raw_df


data_loaded = True

try:
    keywords_df, geo_df, campaign_raw_df = load_data()
except Exception:
    data_loaded = False
    keywords_df = pd.DataFrame()
    geo_df = pd.DataFrame()
    campaign_raw_df = pd.DataFrame()

# ------------------------------------------------
# CLEAN DATA
# ------------------------------------------------

if data_loaded:
    # Keywords
    keywords_df["Month_dt"] = parse_month(keywords_df["Month"])
    keywords_df["Keyword"] = keywords_df["Keyword"].astype(str).str.strip().str.replace('"', "", regex=False)
    keywords_df["Keyword status"] = keywords_df["Keyword status"].astype(str).str.strip()

    keyword_numeric_cols = [
        "Cost", "Clicks", "Impressions", "Conversions",
        "Avg. CPC", "Max. CPC", "Cost / conv.", "Interactions",
        "Interaction rate", "Conv. rate", "Avg. cost"
    ]

    for col in keyword_numeric_cols:
        if col in keywords_df.columns:
            keywords_df[col] = clean_numeric(keywords_df[col])

    enabled_keywords = keywords_df[
        keywords_df["Keyword status"].str.lower() == "enabled"
    ].copy()

    # GEO
    geo_df["Month_dt"] = parse_month(geo_df["Month"])
    geo_df["Location"] = geo_df["Location"].astype(str).str.strip()

    if "Campaign" in geo_df.columns:
        geo_df["Campaign"] = geo_df["Campaign"].astype(str).str.strip()

    geo_numeric_cols = [
        "Cost", "Conversions", "Interactions", "Impr.",
        "Interaction rate", "Conv. rate", "Avg. cost", "Cost / conv."
    ]

    for col in geo_numeric_cols:
        if col in geo_df.columns:
            geo_df[col] = clean_numeric(geo_df[col])

    geo_df = geo_df[geo_df["Location"].apply(is_valid_country)].copy()

    # Campaigns
    campaigns_df = build_campaign_rows(campaign_raw_df)
    if not campaigns_df.empty:
        campaigns_df["Month_dt"] = parse_month(campaigns_df["Month"])
        campaigns_df["Campaign"] = campaigns_df["Campaign"].astype(str).str.strip()

        campaign_numeric_cols = [
            "Cost", "Impr.", "Clicks", "CTR", "Avg. CPC",
            "HS leads", "CPL", "SAL", "Open deal", "Cost per SAL"
        ]
        for col in campaign_numeric_cols:
            if col in campaigns_df.columns:
                campaigns_df[col] = clean_numeric(campaigns_df[col])
    else:
        campaigns_df = pd.DataFrame()

    available_months = sorted(
        pd.concat(
            [
                enabled_keywords["Month_dt"].dropna(),
                geo_df["Month_dt"].dropna(),
                campaigns_df["Month_dt"].dropna() if not campaigns_df.empty else pd.Series(dtype="datetime64[ns]")
            ]
        ).unique()
    )

    available_month_labels = [pd.Timestamp(m).strftime("%b %Y") for m in available_months]
    month_label_to_value = {
        pd.Timestamp(m).strftime("%b %Y"): pd.Timestamp(m) for m in available_months
    }

    available_countries = sorted(geo_df["Location"].dropna().unique().tolist())
else:
    enabled_keywords = pd.DataFrame()
    geo_df = pd.DataFrame()
    campaigns_df = pd.DataFrame()
    available_months = []
    available_month_labels = []
    month_label_to_value = {}
    available_countries = []

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown("""
<div class="glass-card">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🦎 Quicklizard Marketing Dashboard</h1>
    <p style="font-size: 1.1rem; color: rgba(255,255,255,0.82) !important; margin-bottom: 0;">
        Q4-Q1 2026 Marketing Overview for our 3 main channels:
        Google Paid Keywords, Google Organic and Linkedin Campaigns
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Google Paid Keywords", "Google Organic", "LinkedIn Campaigns"]
)

# ------------------------------------------------
# OVERVIEW TAB
# ------------------------------------------------

with tab1:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">Performance Snapshot</div>
        <p style="color: rgba(255,255,255,0.78) !important;">
            This section will act as the executive summary across all major marketing channels for the last 6 months.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Traffic</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder for 6-month traffic trend</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Leads</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder for 6-month lead trend</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Top Performing Channel</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder for strongest channel insight</div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------
# GOOGLE PAID KEYWORDS TAB
# ------------------------------------------------

with tab2:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">Google Paid Keywords</div>
        <p style="color: rgba(255,255,255,0.78) !important;">
            This section combines campaign summary, enabled keyword performance, and country-level GEO analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not data_loaded:
        st.error("Google Paid data files were not found. Please add all 3 files to the data folder.")
        st.code(
            "data/Google Paid Keywords.csv\ndata/Google Paid Locations.csv\ndata/Google Paid Campaigns.csv",
            language="text"
        )
    else:
        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Filters</div>
        """, unsafe_allow_html=True)

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            selected_month_labels = st.multiselect(
                "Dates",
                options=available_month_labels,
                default=available_month_labels,
                placeholder="Select one or more months"
            )

        with filter_col2:
            selected_countries = st.multiselect(
                "Countries",
                options=available_countries,
                default=available_countries,
                placeholder="Select one or more countries"
            )

        st.markdown("""
            <p class="small-note">
                Dates and countries can be selected independently. Country filtering applies to the GEO table and trend. The country list includes only country-level values.
            </p>
        </div>
        """, unsafe_allow_html=True)

        selected_month_values = [
            month_label_to_value[label]
            for label in selected_month_labels
            if label in month_label_to_value
        ]

        if selected_month_values:
            filtered_keywords = enabled_keywords[
                enabled_keywords["Month_dt"].isin(selected_month_values)
            ].copy()

            filtered_geo = geo_df[
                geo_df["Month_dt"].isin(selected_month_values)
            ].copy()

            filtered_campaigns = campaigns_df[
                campaigns_df["Month_dt"].isin(selected_month_values)
            ].copy()
        else:
            filtered_keywords = enabled_keywords.iloc[0:0].copy()
            filtered_geo = geo_df.iloc[0:0].copy()
            filtered_campaigns = campaigns_df.iloc[0:0].copy()

        if selected_countries:
            filtered_geo = filtered_geo[
                filtered_geo["Location"].isin(selected_countries)
            ].copy()
        else:
            filtered_geo = filtered_geo.iloc[0:0].copy()

        # KPI row
        total_spend = filtered_campaigns["Cost"].sum() if not filtered_campaigns.empty else filtered_keywords["Cost"].sum()
        total_clicks = filtered_campaigns["Clicks"].sum() if not filtered_campaigns.empty else filtered_keywords["Clicks"].sum()
        total_hs_leads = filtered_campaigns["HS leads"].sum() if not filtered_campaigns.empty and "HS leads" in filtered_campaigns.columns else 0
        total_open_deals = filtered_campaigns["Open deal"].sum() if not filtered_campaigns.empty and "Open deal" in filtered_campaigns.columns else 0

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Spend</div>
                <div class="metric-value">{fmt_money(total_spend)}</div>
                <div class="metric-delta">Across selected dates</div>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Clicks</div>
                <div class="metric-value">{fmt_number(total_clicks)}</div>
                <div class="metric-delta">Paid search clicks</div>
            </div>
            """, unsafe_allow_html=True)

        with k3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">HS Leads</div>
                <div class="metric-value">{fmt_number(total_hs_leads)}</div>
                <div class="metric-delta">High-level campaign outcome</div>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Open Deals</div>
                <div class="metric-value">{fmt_number(total_open_deals)}</div>
                <div class="metric-delta">Downstream pipeline signal</div>
            </div>
            """, unsafe_allow_html=True)

        # Analysis
        paid_analysis = build_paid_analysis(filtered_campaigns, filtered_keywords)

        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Performance Analysis</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Overall Performance</div>
            <div class="insight-text">{paid_analysis["summary"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Where We Are Not Optimized Enough</div>
            <div class="insight-text">{paid_analysis["efficiency"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Where We Are Missing Opportunities</div>
            <div class="insight-text">{paid_analysis["opportunity"]}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Campaign Summary
        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Campaign Summary</div>
            <p style="color: rgba(255,255,255,0.78) !important;">
                High-level campaign outcomes across spend, traffic, leads, and downstream pipeline.
            </p>
        </div>
        """, unsafe_allow_html=True)

        campaign_trend = pd.DataFrame()
        if not filtered_campaigns.empty:
            campaign_trend = (
                filtered_campaigns.groupby("Month_dt", as_index=False)[
                    ["Cost", "Clicks", "HS leads", "Open deal"]
                ]
                .sum()
                .sort_values("Month_dt")
                .set_index("Month_dt")
            )
            st.markdown("#### Campaign Trend")
            st.line_chart(campaign_trend)

            campaign_table = (
                filtered_campaigns.groupby("Campaign", as_index=False)[
                    ["Impr.", "Clicks", "Cost", "HS leads", "SAL", "Open deal"]
                ]
                .sum()
            )
            campaign_table["CTR %"] = campaign_table.apply(
                lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1
            )
            campaign_table["Avg. CPC"] = campaign_table.apply(
                lambda r: safe_div(r["Cost"], r["Clicks"]), axis=1
            )
            campaign_table["CPL"] = campaign_table.apply(
                lambda r: safe_div(r["Cost"], r["HS leads"]), axis=1
            )
            campaign_table["Cost per SAL"] = campaign_table.apply(
                lambda r: safe_div(r["Cost"], r["SAL"]), axis=1
            )

            campaign_table = campaign_table[
                [
                    "Campaign",
                    "Impr.",
                    "Clicks",
                    "CTR %",
                    "Cost",
                    "Avg. CPC",
                    "HS leads",
                    "CPL",
                    "SAL",
                    "Open deal",
                    "Cost per SAL",
                ]
            ].sort_values(["HS leads", "Open deal", "Cost"], ascending=[False, False, False])

            st.dataframe(
                style_dataframe(campaign_table),
                use_container_width=True,
                height=420
            )
        else:
            st.info("No campaign summary data is available for the selected dates.")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Keyword Section
        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Enabled Keyword Performance</div>
            <p style="color: rgba(255,255,255,0.78) !important;">
                One unified table with all enabled keywords in the selected date range. You can sort every column directly in the table.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_keywords.empty:
            monthly_keywords = (
                filtered_keywords.groupby("Month_dt", as_index=False)[
                    ["Clicks", "Conversions", "Cost", "Impressions"]
                ]
                .sum()
                .sort_values("Month_dt")
                .set_index("Month_dt")
            )

            st.markdown("#### Keyword Trend")
            st.line_chart(monthly_keywords[["Clicks", "Conversions", "Cost"]])

            keyword_table = (
                filtered_keywords.groupby("Keyword", as_index=False)[
                    ["Interactions", "Clicks", "Impressions", "Cost", "Conversions"]
                ]
                .sum()
            )

            keyword_table["CTR %"] = keyword_table.apply(
                lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1
            )
            keyword_table["Conv Rate %"] = keyword_table.apply(
                lambda r: safe_div(r["Conversions"], r["Clicks"]) * 100, axis=1
            )
            keyword_table["Avg. CPC"] = keyword_table.apply(
                lambda r: safe_div(r["Cost"], r["Clicks"]), axis=1
            )
            keyword_table["Max. CPC"] = (
                filtered_keywords.groupby("Keyword", as_index=False)["Max. CPC"].max()["Max. CPC"]
            )
            keyword_table["Cost / Conv."] = keyword_table.apply(
                lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1
            )

            keyword_table = keyword_table[
                [
                    "Keyword",
                    "Impressions",
                    "Clicks",
                    "Interactions",
                    "CTR %",
                    "Conversions",
                    "Conv Rate %",
                    "Cost",
                    "Avg. CPC",
                    "Max. CPC",
                    "Cost / Conv."
                ]
            ].sort_values(["Conversions", "Cost"], ascending=[False, False])

            st.dataframe(
                style_dataframe(keyword_table),
                use_container_width=True,
                height=500
            )
        else:
            st.info("No enabled keyword data is available for the selected dates.")

        st.markdown("<hr>", unsafe_allow_html=True)

        # GEO Section
        st.markdown("""
        <div class="glass-card">
            <div class="section-title">GEO Performance</div>
            <p style="color: rgba(255,255,255,0.78) !important;">
                One unified country-level table only. Non-country rows are excluded automatically. Dates and country filters both apply here.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_geo.empty:
            monthly_geo = (
                filtered_geo.groupby("Month_dt", as_index=False)[
                    ["Interactions", "Conversions", "Cost", "Impr."]
                ]
                .sum()
                .sort_values("Month_dt")
                .set_index("Month_dt")
            )

            st.markdown("#### GEO Trend")
            st.line_chart(monthly_geo[["Interactions", "Conversions", "Cost"]])

            geo_table = (
                filtered_geo.groupby("Location", as_index=False)[
                    ["Impr.", "Interactions", "Cost", "Conversions"]
                ]
                .sum()
            )

            geo_table["Interaction Rate %"] = geo_table.apply(
                lambda r: safe_div(r["Interactions"], r["Impr."]) * 100, axis=1
            )
            geo_table["Conv Rate %"] = geo_table.apply(
                lambda r: safe_div(r["Conversions"], r["Interactions"]) * 100, axis=1
            )
            geo_table["Avg. Cost"] = geo_table.apply(
                lambda r: safe_div(r["Cost"], r["Interactions"]), axis=1
            )
            geo_table["Cost / Conv."] = geo_table.apply(
                lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1
            )

            geo_table = geo_table.rename(columns={"Location": "Country"})
            geo_table = geo_table[
                [
                    "Country",
                    "Impr.",
                    "Interactions",
                    "Interaction Rate %",
                    "Conversions",
                    "Conv Rate %",
                    "Cost",
                    "Avg. Cost",
                    "Cost / Conv."
                ]
            ].sort_values(["Conversions", "Cost"], ascending=[False, False])

            st.dataframe(
                style_dataframe(geo_table),
                use_container_width=True,
                height=500
            )
        else:
            st.info("No country-level GEO data is available for the selected filters.")

# ------------------------------------------------
# GOOGLE ORGANIC TAB
# ------------------------------------------------

with tab3:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">Google Organic</div>
        <p style="color: rgba(255,255,255,0.78) !important;">
            This tab will cover organic website performance coming from Google across engagement and conversion metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Organic Sessions</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder metric</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Engaged Sessions</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder metric</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Conversions</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder metric</div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------
# LINKEDIN CAMPAIGNS TAB
# ------------------------------------------------

with tab4:
    st.markdown("""
    <div class="glass-card">
        <div class="section-title">LinkedIn Campaigns</div>
        <p style="color: rgba(255,255,255,0.78) !important;">
            This tab will focus on paid campaign delivery, clicks, engagement, and lead generation performance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Campaign Impressions</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder metric</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Campaign Clicks</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder metric</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Leads Generated</div>
            <div class="metric-value">--</div>
            <div class="metric-delta">Placeholder metric</div>
        </div>
        """, unsafe_allow_html=True)
