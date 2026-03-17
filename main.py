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
    if pd.isna(a) or pd.isna(b) or b == 0:
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
            {}
                "Month": f"{current_month_name}-{str(current_year)[-2:]}",
                "Campaign": col_b,
                "Cost": row.iloc[2] if len(row) > 2 else None,
                "Impr.": row.iloc[3] if len(row) > 3 else None,
                "Clicks": row.iloc[4] if len(row) > 4 else None,
                "Leads": row.iloc[5] if len(row) > 5 else None,
                "CTR": row.iloc[7] if len(row) > 7 else None,
                "Avg. CPC": row.iloc[8] if len(row) > 8 else None,
                "CPL": row.iloc[9] if len(row) > 9 else None,
                "SAL": row.iloc[11] i
