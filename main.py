from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Quicklizard Marketing Dashboard",
    page_icon="🦎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: white;
    }

    .stApp {
        background: linear-gradient(135deg, #031b3a 0%, #0a3d7a 45%, #1259b8 100%);
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1400px;
    }

    h1, h2, h3, h4, h5, h6, p, li, label, div, span {
        color: white !important;
    }

    .muted {
        color: rgba(255, 255, 255, 0.78) !important;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 1rem;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 1.2rem;
        text-align: left;
        min-height: 140px;
    }

    .metric-label {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.72) !important;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 0.4rem;
        color: white !important;
    }

    .metric-delta {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.82) !important;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: white !important;
    }

    .small-note {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.68) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 10px 18px;
        color: white !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.18) !important;
        color: white !important;
    }

    div[data-baseweb="select"] * {
        color: #0b1f3a !important;
    }

    .stMultiSelect div[data-baseweb="tag"] {
        background-color: rgba(255,255,255,0.18) !important;
    }

    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.15);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# HELPERS
# -----------------------------
def parse_month_column(series):
    return pd.to_datetime(series, format="%b-%y", errors="coerce")


def clean_numeric(series):
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("--", "", regex=False)
        .str.strip()
        .replace("", pd.NA)
        .astype(float)
    )


def format_number(value, decimals=0):
    if pd.isna(value):
        return "--"
    return f"{value:,.{decimals}f}"


def safe_divide(numerator, denominator):
    if denominator == 0 or pd.isna(denominator):
        return 0
    return numerator / denominator


@st.cache_data
def load_google_paid_data():
    keywords_path = Path("data/Google Paid Keywords.csv")
    locations_path = Path("data/Google Paid Locations.csv")

    keywords_df = pd.read_csv(keywords_path)
    locations_df = pd.read_csv(locations_path)

    return keywords_df, locations_df


# -----------------------------
# LOAD DATA
# -----------------------------
paid_data_loaded = False
keywords_df = pd.DataFrame()
locations_df = pd.DataFrame()
enabled_keywords_df = pd.DataFrame()
all_months = []

try:
    keywords_df, locations_df = load_google_paid_data()
    paid_data_loaded = True
except Exception:
    paid_data_loaded = False

if paid_data_loaded:
    # Keywords data
    keywords_df["Month_dt"] = parse_month_column(keywords_df["Month"])
    keywords_df["Keyword status"] = keywords_df["Keyword status"].astype(str).str.strip()
    keywords_df["Keyword"] = (
        keywords_df["Keyword"].astype(str).str.strip().str.replace('"', "", regex=False)
    )

    keyword_numeric_cols = [
        "Interactions",
        "Avg. cost",
        "Cost",
        "Impressions",
        "Clicks",
        "Conversions",
        "Avg. CPC",
        "Cost / conv.",
        "Max. CPC",
    ]
    for col in keyword_numeric_cols:
        if col in keywords_df.columns:
            keywords_df[col] = clean_numeric(keywords_df[col])

    if "Interaction rate" in keywords_df.columns:
        keywords_df["Interaction rate"] = clean_numeric(keywords_df["Interaction rate"])

    if "Conv. rate" in keywords_df.columns:
        keywords_df["Conv. rate"] = clean_numeric(keywords_df["Conv. rate"])

    enabled_keywords_df = keywords_df[
        keywords_df["Keyword status"].str.lower() == "enabled"
    ].copy()

    # Locations data
    locations_df["Month_dt"] = parse_month_column(locations_df["Month"])
    locations_df["Location"] = locations_df["Location"].astype(str).str.strip()

    if "Campaign" in locations_df.columns:
        locations_df["Campaign"] = locations_df["Campaign"].astype(str).str.strip()

    location_numeric_cols = [
        "Impr.",
        "Interactions",
        "Avg. cost",
        "Cost",
        "Conversions",
        "Cost / conv.",
    ]
    for col in location_numeric_cols:
        if col in locations_df.columns:
            locations_df[col] = clean_numeric(locations_df[col])

    if "Interaction rate" in locations_df.columns:
        locations_df["Interaction rate"] = clean_numeric(locations_df["Interaction rate"])

    if "Conv. rate" in locations_df.columns:
        locations_df["Conv. rate"] = clean_numeric(locations_df["Conv. rate"])

    all_months = sorted(
        pd.concat(
            [
                enabled_keywords_df["Month_dt"].dropna(),
                locations_df["Month_dt"].dropna(),
            ]
        ).unique()
    )


# -----------------------------
# HERO
# -----------------------------
st.markdown(
    """
    <div class="glass-card">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">
            🦎 Quicklizard Marketing Dashboard
        </h1>
        <p class="muted" style="font-size: 1.15rem; max-width: 850px;">
            Q4-Q1 2026 Marketing Overview for our 3 main channels:
            Google Paid Keywords, Google Organic and Linkedin Campaigns
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Google Paid Keywords", "Google Organic", "LinkedIn Campaigns"]
)

# -----------------------------
# OVERVIEW TAB
# -----------------------------
with tab1:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Performance Snapshot</div>
            <p class="muted">
                This section will act as the executive summary across all major marketing channels for the last 6 months.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Total Traffic</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder for 6-month traffic trend</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Total Leads</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder for 6-month lead trend</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Top Performing Channel</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder for strongest channel insight</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# GOOGLE PAID KEYWORDS TAB
# -----------------------------
with tab2:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Google Paid Keywords</div>
            <p class="muted">
                This section combines paid keyword and GEO performance across impressions, clicks, cost, and conversions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not paid_data_loaded:
        st.error(
            "Google Paid data files were not found. Please add both files to the data folder."
        )
        st.code(
            "data/Google Paid Keywords.csv\ndata/Google Paid Locations.csv",
            language="text",
        )
    else:
        # -----------------------------
        # FILTERS
        # -----------------------------
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Filters</div>
            """,
            unsafe_allow_html=True,
        )

        filter_col1, filter_col2 = st.columns([1.2, 1.2])

        with filter_col1:
            if len(all_months) > 0:
                month_labels = [pd.Timestamp(m).strftime("%b %Y") for m in all_months]
                default_range = (0, len(month_labels) - 1)

                selected_range = st.select_slider(
                    "Date Range",
                    options=list(range(len(month_labels))),
                    value=default_range,
                    format_func=lambda x: month_labels[x],
                )

                selected_start = pd.Timestamp(all_months[selected_range[0]])
                selected_end = pd.Timestamp(all_months[selected_range[1]])
            else:
                selected_start = None
                selected_end = None
                st.info("No valid dates found in the uploaded data.")

        with filter_col2:
            all_locations = sorted(locations_df["Location"].dropna().unique().tolist())
            selected_countries = st.multiselect(
                "Countries / GEOs",
                options=all_locations,
                default=all_locations,
            )

        st.markdown(
            """
            <p class="small-note">
                Date filters apply to both keyword and GEO data. Country filters apply only to GEO sections because the keyword file does not include a country field.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Apply filters
        filtered_keywords = enabled_keywords_df.copy()
        filtered_locations = locations_df.copy()

        if selected_start is not None and selected_end is not None:
            filtered_keywords = filtered_keywords[
                (filtered_keywords["Month_dt"] >= selected_start)
                & (filtered_keywords["Month_dt"] <= selected_end)
            ].copy()

            filtered_locations = filtered_locations[
                (filtered_locations["Month_dt"] >= selected_start)
                & (filtered_locations["Month_dt"] <= selected_end)
            ].copy()

        if selected_countries:
            filtered_locations = filtered_locations[
                filtered_locations["Location"].isin(selected_countries)
            ].copy()
        else:
            filtered_locations = filtered_locations.iloc[0:0].copy()

        # -----------------------------
        # HEADLINE KPI CARDS
        # -----------------------------
        total_spend = filtered_keywords["Cost"].sum()
        total_conversions = filtered_keywords["Conversions"].sum()
        avg_cpa = safe_divide(total_spend, total_conversions)
        total_clicks = filtered_keywords["Clicks"].sum()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Total Spend</div>
                    <div class="metric-value">${format_number(total_spend, 2)}</div>
                    <div class="metric-delta">Enabled keywords only</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Total Conversions</div>
                    <div class="metric-value">{format_number(total_conversions, 0)}</div>
                    <div class="metric-delta">Across selected date range</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Avg CPA</div>
                    <div class="metric-value">${format_number(avg_cpa, 2)}</div>
                    <div class="metric-delta">Cost per conversion</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with kpi4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Total Clicks</div>
                    <div class="metric-value">{format_number(total_clicks, 0)}</div>
                    <div class="metric-delta">Paid keyword clicks</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # -----------------------------
        # TOP SECTION: KEYWORDS
        # -----------------------------
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Top Performing Keywords</div>
                <p class="muted">
                    Top section is dedicated to keyword performance. Paused keywords are excluded automatically.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        kw_chart_col1, kw_chart_col2 = st.columns(2)

        with kw_chart_col1:
            monthly_keywords = (
                filtered_keywords.groupby("Month_dt", as_index=False)[
                    ["Clicks", "Conversions", "Cost", "Impressions"]
                ]
                .sum()
                .sort_values("Month_dt")
            )

            if not monthly_keywords.empty:
                keyword_trend = monthly_keywords.set_index("Month_dt")[
                    ["Clicks", "Conversions", "Cost"]
                ]
                st.markdown("#### Keyword Trend")
                st.line_chart(keyword_trend)
            else:
                st.info("No keyword trend data available for the selected date range.")

        with kw_chart_col2:
            top_keywords = (
                filtered_keywords.groupby("Keyword", as_index=False)[
                    ["Clicks", "Impressions", "Cost", "Conversions"]
                ]
                .sum()
            )
            top_keywords["CTR %"] = top_keywords.apply(
                lambda row: safe_divide(row["Clicks"], row["Impressions"]) * 100,
                axis=1,
            )
            top_keywords["Cost / Conv."] = top_keywords.apply(
                lambda row: safe_divide(row["Cost"], row["Conversions"]),
                axis=1,
            )

            top_keywords_by_conv = top_keywords.sort_values(
                ["Conversions", "Clicks"],
                ascending=[False, False],
            ).head(10)

            st.markdown("#### Top Keywords by Conversions")
            st.dataframe(
                top_keywords_by_conv[
                    ["Keyword", "Conversions", "Clicks", "Impressions", "CTR %", "Cost", "Cost / Conv."]
                ].style.format(
                    {
                        "Conversions": "{:,.0f}",
                        "Clicks": "{:,.0f}",
                        "Impressions": "{:,.0f}",
                        "CTR %": "{:,.2f}%",
                        "Cost": "${:,.2f}",
                        "Cost / Conv.": "${:,.2f}",
                    }
                ),
                use_container_width=True,
            )

        st.markdown("#### Top Keywords by Spend")
        top_keywords_by_spend = top_keywords.sort_values("Cost", ascending=False).head(10)
        st.dataframe(
            top_keywords_by_spend[
                ["Keyword", "Cost", "Conversions", "Clicks", "CTR %", "Cost / Conv."]
            ].style.format(
                {
                    "Cost": "${:,.2f}",
                    "Conversions": "{:,.0f}",
                    "Clicks": "{:,.0f}",
                    "CTR %": "{:,.2f}%",
                    "Cost / Conv.": "${:,.2f}",
                }
            ),
            use_container_width=True,
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # -----------------------------
        # BOTTOM SECTION: GEOS
        # -----------------------------
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">GEO Performance</div>
                <p class="muted">
                    Bottom section is dedicated to country-level performance, with country filtering enabled.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        geo_col1, geo_col2 = st.columns(2)

        with geo_col1:
            monthly_geo = (
                filtered_locations.groupby("Month_dt", as_index=False)[
                    ["Interactions", "Conversions", "Cost", "Impr."]
                ]
                .sum()
                .sort_values("Month_dt")
            )

            if not monthly_geo.empty:
                geo_trend = monthly_geo.set_index("Month_dt")[
                    ["Interactions", "Conversions", "Cost"]
                ]
                st.markdown("#### GEO Trend")
                st.line_chart(geo_trend)
            else:
                st.info("No GEO trend data available for the selected filters.")

        with geo_col2:
            top_countries = (
                filtered_locations.groupby("Location", as_index=False)[
                    ["Impr.", "Interactions", "Cost", "Conversions"]
                ]
                .sum()
            )
            top_countries["Interaction Rate %"] = top_countries.apply(
                lambda row: safe_divide(row["Interactions"], row["Impr."]) * 100,
                axis=1,
            )
            top_countries["Cost / Conv."] = top_countries.apply(
                lambda row: safe_divide(row["Cost"], row["Conversions"]),
                axis=1,
            )

            top_countries_by_conv = top_countries.sort_values(
                ["Conversions", "Interactions"],
                ascending=[False, False],
            ).head(10)

            st.markdown("#### Top Countries by Conversions")
            st.dataframe(
                top_countries_by_conv[
                    ["Location", "Conversions", "Interactions", "Impr.", "Interaction Rate %", "Cost", "Cost / Conv."]
                ].style.format(
                    {
                        "Conversions": "{:,.0f}",
                        "Interactions": "{:,.0f}",
                        "Impr.": "{:,.0f}",
                        "Interaction Rate %": "{:,.2f}%",
                        "Cost": "${:,.2f}",
                        "Cost / Conv.": "${:,.2f}",
                    }
                ),
                use_container_width=True,
            )

        st.markdown("#### Top Countries by Spend")
        top_countries_by_spend = top_countries.sort_values("Cost", ascending=False).head(10)
        st.dataframe(
            top_countries_by_spend[
                ["Location", "Cost", "Conversions", "Interactions", "Interaction Rate %", "Cost / Conv."]
            ].style.format(
                {
                    "Cost": "${:,.2f}",
                    "Conversions": "{:,.0f}",
                    "Interactions": "{:,.0f}",
                    "Interaction Rate %": "{:,.2f}%",
                    "Cost / Conv.": "${:,.2f}",
                }
            ),
            use_container_width=True,
        )

# -----------------------------
# GOOGLE ORGANIC TAB
# -----------------------------
with tab3:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Google Organic</div>
            <p class="muted">
                This tab will cover organic website performance coming from Google across engagement and conversion metrics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Organic Sessions</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Engaged Sessions</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Conversions</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# LINKEDIN CAMPAIGNS TAB
# -----------------------------
with tab4:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">LinkedIn Campaigns</div>
            <p class="muted">
                This tab will focus on paid campaign delivery, clicks, engagement, and lead generation performance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Campaign Impressions</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Campaign Clicks</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Leads Generated</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
