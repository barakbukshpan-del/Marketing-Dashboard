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
    padding: 1.35rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 1.05rem;
    min-height: 122px;
}

.metric-label {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.72) !important;
    margin-bottom: 0.4rem;
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
    margin-bottom: 0.25rem;
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
    margin-bottom: 0.45rem;
    color: white !important;
}

.insight-text, .insight-text li {
    font-size: 0.95rem;
    line-height: 1.4;
    color: rgba(255,255,255,0.87) !important;
}

.green-chip {
    display: inline-block;
    background: linear-gradient(135deg, #0b7a42 0%, #11a15a 100%);
    color: white !important;
    border-radius: 999px;
    padding: 0.45rem 0.85rem;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.25rem;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 0.25rem;
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
    background: linear-gradient(135deg, #0b7a42 0%, #11a15a 100%) !important;
    color: white !important;
    border-radius: 10px !important;
}

div[role="radiogroup"] label {
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
    padding: 0.25rem 0.7rem !important;
    margin-right: 0.35rem;
    border: 1px solid rgba(255,255,255,0.12);
}

hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.15);
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""",
    unsafe_allow_html=True,
)

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


def bullets_to_html(items):
    items = items[:4]
    li_html = "".join([f"<li>{item}</li>" for item in items])
    return f"<ul>{li_html}</ul>"


def is_valid_country(location_value: str) -> bool:
    if pd.isna(location_value):
        return False
    value = str(location_value).strip()
    if value == "" or value.startswith("Total:") or "," in value:
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
    return value not in invalid_values


def map_geo_region(country: str) -> str:
    if pd.isna(country):
        return "Rest of World"
    country = str(country).strip()

    mapping = {
        "United Kingdom": "UK",
        "United States": "North America",
        "Canada": "North America",
        "Germany": "DACH + BeNeLux",
        "Austria": "DACH + BeNeLux",
        "Switzerland": "DACH + BeNeLux",
        "Belgium": "DACH + BeNeLux",
        "Netherlands": "DACH + BeNeLux",
        "Luxembourg": "DACH + BeNeLux",
        "Denmark": "Nordics",
        "Sweden": "Nordics",
        "Norway": "Nordics",
        "Finland": "Nordics",
        "Iceland": "Nordics",
        "Australia": "ANZ",
        "New Zealand": "ANZ",
        "France": "Rest of Europe",
        "Italy": "Rest of Europe",
        "Spain": "Rest of Europe",
        "Portugal": "Rest of Europe",
        "Ireland": "Rest of Europe",
        "Czechia": "Rest of Europe",
        "Czech Republic": "Rest of Europe",
        "Slovakia": "Rest of Europe",
        "Hungary": "Rest of Europe",
        "Poland": "Rest of Europe",
        "Romania": "Rest of Europe",
        "Bulgaria": "Rest of Europe",
        "Croatia": "Rest of Europe",
        "Slovenia": "Rest of Europe",
        "Greece": "Rest of Europe",
        "Estonia": "Rest of Europe",
        "Latvia": "Rest of Europe",
        "Lithuania": "Rest of Europe",
        "Malta": "Rest of Europe",
        "Cyprus": "Rest of Europe",
    }
    return mapping.get(country, "Rest of World")


def build_google_campaign_rows(raw_df: pd.DataFrame) -> pd.DataFrame:
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

        if c1 in ["Campaign", "Total", "", "nan"] or current_month_name is None:
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


def build_linkedin_rows(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy().reset_index(drop=True)

    month_map = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
    month_map.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})

    rows = []
    current_month_name = None
    current_year = 2025
    last_month_num = None

    for _, row in df.iterrows():
        col_a = str(row.iloc[0]).strip() if len(row) > 0 and pd.notna(row.iloc[0]) else ""
        col_b = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""

        if col_a:
            month_token = col_a.split()[0].lower()
            if month_token in month_map:
                month_num = month_map[month_token]
                if last_month_num is not None and month_num < last_month_num:
                    current_year += 1
                last_month_num = month_num
                current_month_name = calendar.month_abbr[month_num]
                continue

        if current_month_name is None:
            continue

        if col_b == "" or col_b.lower() == "campaign" or col_b.upper() == "TOTAL":
            continue

        rows.append(
            {
                "Month": f"{current_month_name}-{str(current_year)[-2:]}",
                "Campaign": col_b,
                "Cost": row.iloc[2] if len(row) > 2 else None,
                "Impr.": row.iloc[3] if len(row) > 3 else None,
                "Clicks": row.iloc[4] if len(row) > 4 else None,
                "Leads": row.iloc[5] if len(row) > 5 else None,
                "CTR": row.iloc[7] if len(row) > 7 else None,
                "Avg. CPC": row.iloc[8] if len(row) > 8 else None,
                "CPL": row.iloc[9] if len(row) > 9 else None,
                "SAL": row.iloc[11] if len(row) > 11 else None,
                "Open deal": row.iloc[12] if len(row) > 12 else None,
                "Cost per SAL": row.iloc[13] if len(row) > 13 else None,
            }
        )

    return pd.DataFrame(rows)


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
    label_cols = {"Keyword", "Campaign", "Country", "Region"}
    int_cols = [c for c in df.columns if c not in pct_cols and c not in money_cols and c not in label_cols]

    format_map = {}
    for c in pct_cols:
        format_map[c] = lambda x: "--" if pd.isna(x) else f"{round(x)}%"
    for c in money_cols:
        format_map[c] = lambda x: "--" if pd.isna(x) else f"${round(x):,}"
    for c in int_cols:
        format_map[c] = lambda x: "--" if pd.isna(x) else f"{round(x):,}"

    return df.style.format(format_map)


def build_paid_analysis(campaign_df: pd.DataFrame, keyword_df: pd.DataFrame, geo_df: pd.DataFrame):
    bullets = {"overall": [], "optimization": [], "opportunity": []}

    if not campaign_df.empty:
        spend = campaign_df["Cost"].sum()
        clicks = campaign_df["Clicks"].sum()
        impr = campaign_df["Impr."].sum()
        hs_leads = campaign_df["HS leads"].sum()
        sal = campaign_df["SAL"].sum()
        deals = campaign_df["Open deal"].sum()

        bullets["overall"].append(
            f"{fmt_money(spend)} spend drove {fmt_number(clicks)} clicks, {fmt_number(hs_leads)} HS leads, {fmt_number(sal)} SALs, and {fmt_number(deals)} open deals."
        )
        bullets["overall"].append(
            f"CTR is {fmt_pct(safe_div(clicks, impr) * 100)}, CPL is {fmt_money(safe_div(spend, hs_leads))}, and cost per SAL is {fmt_money(safe_div(spend, sal))}."
        )

        campaign_rank = campaign_df.groupby("Campaign", as_index=False)[["Cost", "Clicks", "Impr.", "HS leads", "SAL", "Open deal"]].sum()
        campaign_rank["CTR %"] = campaign_rank.apply(lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1)

        best = campaign_rank.sort_values(["Open deal", "SAL", "HS leads"], ascending=[False, False,
