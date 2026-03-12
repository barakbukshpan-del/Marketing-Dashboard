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
    font-size: 0.96rem;
    line-height: 1.55;
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

.filter-summary {
    background: linear-gradient(135deg, rgba(11,122,66,0.92) 0%, rgba(17,161,90,0.92) 100%);
    color: white !important;
    border-radius: 14px;
    padding: 0.85rem 1rem;
    border: 1px solid rgba(255,255,255,0.12);
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

        if c1 in ["Campaign", "Total", "", "nan"]:
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


def bullets_to_html(items):
    li_html = "".join([f"<li>{item}</li>" for item in items])
    return f"<ul>{li_html}</ul>"


def build_paid_analysis(campaign_df: pd.DataFrame, keyword_df: pd.DataFrame, geo_df: pd.DataFrame):
    bullets = {
        "overall": [],
        "optimization": [],
        "opportunity": [],
    }

    if not campaign_df.empty:
        total_spend = campaign_df["Cost"].sum()
        total_clicks = campaign_df["Clicks"].sum()
        total_impr = campaign_df["Impr."].sum()
        total_hs_leads = campaign_df["HS leads"].sum()
        total_sal = campaign_df["SAL"].sum()
        total_open_deals = campaign_df["Open deal"].sum()

        overall_ctr = safe_div(total_clicks, total_impr) * 100
        blended_cpl = safe_div(total_spend, total_hs_leads)
        blended_cost_per_sal = safe_div(total_spend, total_sal)

        bullets["overall"].append(
            f"Paid search delivered {fmt_money(total_spend)} in spend, {fmt_number(total_clicks)} clicks, {fmt_number(total_hs_leads)} HS leads, {fmt_number(total_sal)} SALs, and {fmt_number(total_open_deals)} open deals in the selected period."
        )
        bullets["overall"].append(
            f"Blended CTR is {fmt_pct(overall_ctr)}, blended CPL is {fmt_money(blended_cpl)}, and blended cost per SAL is {fmt_money(blended_cost_per_sal)}."
        )

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

        best_campaign = campaign_rank.sort_values(
            ["Open deal", "SAL", "HS leads"], ascending=[False, False, False]
        ).head(1)

        if not best_campaign.empty:
            row = best_campaign.iloc[0]
            bullets["overall"].append(
                f"The strongest campaign currently is {row['Campaign']}, generating {fmt_number(row['HS leads'])} HS leads, {fmt_number(row['SAL'])} SALs, and {fmt_number(row['Open deal'])} open deals."
            )

        inefficient_campaigns = campaign_rank[
            (campaign_rank["Cost"] > campaign_rank["Cost"].median()) &
            (campaign_rank["HS leads"] <= campaign_rank["HS leads"].median())
        ].sort_values("Cost", ascending=False)

        if not inefficient_campaigns.empty:
            names = inefficient_campaigns["Campaign"].head(3).tolist()
            bullets["optimization"].append(
                f"Highest spend concentration with weaker downstream efficiency is showing up in {', '.join(names)}. These campaigns are taking budget without returning enough HS lead volume."
            )

        pipeline_leak = campaign_rank[
            (campaign_rank["HS leads"] > 0) &
            (campaign_rank["Open deal"] == 0)
        ].sort_values(["HS leads", "SAL"], ascending=[False, False])

        if not pipeline_leak.empty:
            names = pipeline_leak["Campaign"].head(3).tolist()
            bullets["optimization"].append(
                f"There is lead-to-pipeline leakage in {', '.join(names)}, where top-of-funnel activity is not translating into open deal creation."
            )

        strong_lead_weak_ctr = campaign_rank[
            (campaign_rank["HS leads"] > campaign_rank["HS leads"].median()) &
            (campaign_rank["CTR %"] < campaign_rank["CTR %"].median())
        ].sort_values("HS leads", ascending=False)

        if not strong_lead_weak_ctr.empty:
            names = strong_lead_weak_ctr["Campaign"].head(3).tolist()
            bullets["opportunity"].append(
                f"{', '.join(names)} appear to convert despite lower CTR. That suggests message efficiency could still be improved and scaled if click capture gets stronger."
            )

    if not keyword_df.empty:
        kw = keyword_df.groupby("Keyword", as_index=False)[
            ["Cost", "Clicks", "Impressions", "Conversions"]
        ].sum()

        kw["CTR %"] = kw.apply(lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1)
        kw["Conv Rate %"] = kw.apply(lambda r: safe_div(r["Conversions"], r["Clicks"]) * 100, axis=1)
        kw["Cost / Conv."] = kw.apply(lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1)

        best_kw = kw.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
        if not best_kw.empty:
            names = best_kw["Keyword"].tolist()
            bullets["overall"].append(
                f"Top converting enabled keywords are {', '.join(names)}."
            )

        costly_kw = kw[
            (kw["Cost"] > kw["Cost"].median()) &
            (kw["Conversions"] <= kw["Conversions"].median())
        ].sort_values("Cost", ascending=False)

        if not costly_kw.empty:
            names = costly_kw["Keyword"].head(3).tolist()
            bullets["optimization"].append(
                f"The most obvious keyword inefficiency is concentrated in {', '.join(names)}, where spend is elevated but conversion output is not keeping up."
            )

        high_impr_low_ctr = kw[
            (kw["Impressions"] > kw["Impressions"].median()) &
            (kw["CTR %"] < kw["CTR %"].median())
        ].sort_values("Impressions", ascending=False)

        if not high_impr_low_ctr.empty:
            names = high_impr_low_ctr["Keyword"].head(3).tolist()
            bullets["opportunity"].append(
                f"The cleanest missed keyword opportunity is in {', '.join(names)}, which have visibility but are not capturing enough clicks. That usually points to ad copy, intent matching, or offer framing issues."
            )

    if not geo_df.empty:
        geo_rollup = geo_df.groupby("Location", as_index=False)[
            ["Cost", "Interactions", "Impr.", "Conversions"]
        ].sum()

        geo_rollup["Interaction Rate %"] = geo_rollup.apply(
            lambda r: safe_div(r["Interactions"], r["Impr."]) * 100, axis=1
        )
        geo_rollup["Conv Rate %"] = geo_rollup.apply(
            lambda r: safe_div(r["Conversions"], r["Interactions"]) * 100, axis=1
        )
        geo_rollup["Cost / Conv."] = geo_rollup.apply(
            lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1
        )

        best_geo = geo_rollup.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
        if not best_geo.empty:
            names = best_geo["Location"].tolist()
            bullets["overall"].append(
                f"Top GEOs by conversion contribution are {', '.join(names)}."
            )

        weak_geo = geo_rollup[
            (geo_rollup["Cost"] > geo_rollup["Cost"].median()) &
            (geo_rollup["Conversions"] <= geo_rollup["Conversions"].median())
        ].sort_values("Cost", ascending=False)

        if not weak_geo.empty:
            names = weak_geo["Location"].head(3).tolist()
            bullets["optimization"].append(
                f"At the GEO level, the weakest efficiency appears in {', '.join(names)}, where spend is not converting proportionally."
            )

        strong_geo_low_spend = geo_rollup[
            (geo_rollup["Conversions"] > geo_rollup["Conversions"].median()) &
            (geo_rollup["Cost"] < geo_rollup["Cost"].median())
        ].sort_values("Conversions", ascending=False)

        if not strong_geo_low_spend.empty:
            names = strong_geo_low_spend["Location"].head(3).tolist()
            bullets["opportunity"].append(
                f"There may be room to scale stronger GEO pockets such as {', '.join(names)}, which are converting relatively well without being the biggest spend centers."
            )

    for key in bullets:
        if not bullets[key]:
            if key == "overall":
                bullets[key] = ["No strong high-confidence summary is available yet for the selected slice."]
            elif key == "optimization":
                bullets[key] = ["No major outlier is standing out in this filtered view."]
            else:
                bullets[key] = ["No single missed opportunity dominates the current filtered view."]

    return bullets


def build_campaign_section_analysis(campaign_df: pd.DataFrame):
    bullets = []

    if campaign_df.empty:
        return ["No campaign-level data is available for the selected filters."]

    summary = campaign_df.groupby("Campaign", as_index=False)[
        ["Cost", "Clicks", "Impr.", "HS leads", "SAL", "Open deal"]
    ].sum()

    summary["CTR %"] = summary.apply(lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1)
    summary["CPL"] = summary.apply(lambda r: safe_div(r["Cost"], r["HS leads"]), axis=1)
    summary["Cost per SAL"] = summary.apply(lambda r: safe_div(r["Cost"], r["SAL"]), axis=1)

    top_spend = summary.sort_values("Cost", ascending=False).head(1)
    top_pipeline = summary.sort_values(["Open deal", "SAL", "HS leads"], ascending=[False, False, False]).head(1)
    weak_eff = summary[
        (summary["Cost"] > summary["Cost"].median()) &
        (summary["HS leads"] <= summary["HS leads"].median())
    ].sort_values("Cost", ascending=False).head(3)

    if not top_spend.empty:
        row = top_spend.iloc[0]
        bullets.append(
            f"{row['Campaign']} is the highest-spend campaign at {fmt_money(row['Cost'])}, generating {fmt_number(row['HS leads'])} HS leads and {fmt_number(row['Open deal'])} open deals."
        )

    if not top_pipeline.empty:
        row = top_pipeline.iloc[0]
        bullets.append(
            f"{row['Campaign']} is currently the strongest downstream campaign, leading on pipeline outcomes with {fmt_number(row['Open deal'])} open deals."
        )

    if not weak_eff.empty:
        bullets.append(
            f"Campaign efficiency pressure is concentrated in {', '.join(weak_eff['Campaign'].tolist())}, where spend is relatively high versus HS lead output."
        )

    low_ctr_strong_lead = summary[
        (summary["CTR %"] < summary["CTR %"].median()) &
        (summary["HS leads"] > summary["HS leads"].median())
    ].sort_values("HS leads", ascending=False).head(2)

    if not low_ctr_strong_lead.empty:
        bullets.append(
            f"{', '.join(low_ctr_strong_lead['Campaign'].tolist())} appear to outperform despite lower CTR, which suggests room to scale if click capture improves."
        )

    pipeline_gap = summary[
        (summary["HS leads"] > 0) &
        (summary["Open deal"] == 0)
    ].sort_values(["HS leads", "SAL"], ascending=[False, False]).head(3)

    if not pipeline_gap.empty:
        bullets.append(
            f"Lead-to-pipeline leakage is visible in {', '.join(pipeline_gap['Campaign'].tolist())}, where lead generation is not converting into open deal creation."
        )

    return bullets or ["No strong campaign anomaly stands out in the current filtered view."]


def build_keyword_section_analysis(keyword_df: pd.DataFrame):
    bullets = []

    if keyword_df.empty:
        return ["No keyword-level data is available for the selected filters."]

    kw = keyword_df.groupby("Keyword", as_index=False)[
        ["Cost", "Clicks", "Impressions", "Conversions"]
    ].sum()

    kw["CTR %"] = kw.apply(lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1)
    kw["Conv Rate %"] = kw.apply(lambda r: safe_div(r["Conversions"], r["Clicks"]) * 100, axis=1)
    kw["Cost / Conv."] = kw.apply(lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1)

    top_conv = kw.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
    if not top_conv.empty:
        bullets.append(
            f"Top keyword performers by conversion are {', '.join(top_conv['Keyword'].tolist())}."
        )

    costly_kw = kw[
        (kw["Cost"] > kw["Cost"].median()) &
        (kw["Conversions"] <= kw["Conversions"].median())
    ].sort_values("Cost", ascending=False).head(3)

    if not costly_kw.empty:
        bullets.append(
            f"The clearest keyword inefficiency sits in {', '.join(costly_kw['Keyword'].tolist())}, where spend is heavier than conversion return."
        )

    high_vis_low_ctr = kw[
        (kw["Impressions"] > kw["Impressions"].median()) &
        (kw["CTR %"] < kw["CTR %"].median())
    ].sort_values("Impressions", ascending=False).head(3)

    if not high_vis_low_ctr.empty:
        bullets.append(
            f"The best missed click-through opportunity appears in {', '.join(high_vis_low_ctr['Keyword'].tolist())}, where visibility exists but click capture is underperforming."
        )

    strong_conv_low_click = kw[
        (kw["Conv Rate %"] > kw["Conv Rate %"].median()) &
        (kw["Clicks"] < kw["Clicks"].median())
    ].sort_values("Conv Rate %", ascending=False).head(3)

    if not strong_conv_low_click.empty:
        bullets.append(
            f"{', '.join(strong_conv_low_click['Keyword'].tolist())} look like under-scaled terms with better-than-average conversion efficiency but limited click volume."
        )

    return bullets or ["No strong keyword anomaly stands out in the current filtered view."]


def build_global_section_analysis(geo_df: pd.DataFrame, campaign_df: pd.DataFrame, keyword_df: pd.DataFrame):
    bullets = []

    if geo_df.empty:
        return ["No global country-level data is available for the selected filters."]

    geo = geo_df.groupby(["Region", "Location"], as_index=False)[
        ["Cost", "Interactions", "Impr.", "Conversions"]
    ].sum()

    geo["Interaction Rate %"] = geo.apply(lambda r: safe_div(r["Interactions"], r["Impr."]) * 100, axis=1)
    geo["Conv Rate %"] = geo.apply(lambda r: safe_div(r["Conversions"], r["Interactions"]) * 100, axis=1)
    geo["Cost / Conv."] = geo.apply(lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1)

    top_country = geo.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
    if not top_country.empty:
        bullets.append(
            f"Top country contributors are {', '.join(top_country['Location'].tolist())}."
        )

    weak_country = geo[
        (geo["Cost"] > geo["Cost"].median()) &
        (geo["Conversions"] <= geo["Conversions"].median())
    ].sort_values("Cost", ascending=False).head(3)

    if not weak_country.empty:
        bullets.append(
            f"The weakest country-level efficiency is showing up in {', '.join(weak_country['Location'].tolist())}, where spend is not converting proportionally."
        )

    strong_country_low_spend = geo[
        (geo["Conversions"] > geo["Conversions"].median()) &
        (geo["Cost"] < geo["Cost"].median())
    ].sort_values("Conversions", ascending=False).head(3)

    if not strong_country_low_spend.empty:
        bullets.append(
            f"The strongest scale candidates appear to be {', '.join(strong_country_low_spend['Location'].tolist())}, which are producing conversions without being the biggest spend centers."
        )

    region_rollup = geo.groupby("Region", as_index=False)[["Cost", "Conversions"]].sum()
    region_rollup["Cost / Conv."] = region_rollup.apply(lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1)

    best_region = region_rollup.sort_values(["Conversions", "Cost / Conv."], ascending=[False, True]).head(1)
    if not best_region.empty:
        bullets.append(
            f"{best_region.iloc[0]['Region']} is the strongest region-level contributor in the current view."
        )

    if not campaign_df.empty and not keyword_df.empty:
        bullets.append(
            "Global performance should be read alongside campaign and keyword efficiency, since strong campaign or keyword output may still be concentrated in only a few GEO pockets."
        )

    return bullets or ["No strong global anomaly stands out in the current filtered view."]

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
    geo_df["Region"] = geo_df["Location"].apply(map_geo_region)

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

    q4_2025_labels = [label for label in available_month_labels if label in ["Oct 2025", "Nov 2025", "Dec 2025"]]
    q1_2026_labels = [label for label in available_month_labels if label in ["Jan 2026", "Feb 2026", "Mar 2026"]]

    available_regions = [
        "UK",
        "North America",
        "DACH + BeNeLux",
        "Nordics",
        "ANZ",
        "Rest of Europe",
        "Rest of World",
    ]
else:
    enabled_keywords = pd.DataFrame()
    geo_df = pd.DataFrame()
    campaigns_df = pd.DataFrame()
    available_months = []
    available_month_labels = []
    month_label_to_value = {}
    q4_2025_labels = []
    q1_2026_labels = []
    available_regions = []

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
# GOOGLE PAID TAB
# ------------------------------------------------

with tab2:
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

        date_col, region_col = st.columns(2)

        with date_col:
            st.markdown("**Dates**")
            date_mode = st.radio(
                "Date Preset",
                options=["All", "Q4 2025", "Q1 2026", "Custom"],
                horizontal=True,
                label_visibility="collapsed"
            )

            if date_mode == "All":
                selected_month_labels = available_month_labels
                st.markdown('<div class="green-chip">All available months selected</div>', unsafe_allow_html=True)
            elif date_mode == "Q4 2025":
                selected_month_labels = q4_2025_labels
                st.markdown('<div class="green-chip">Q4 2025 selected</div>', unsafe_allow_html=True)
            elif date_mode == "Q1 2026":
                selected_month_labels = q1_2026_labels
                st.markdown('<div class="green-chip">Q1 2026 selected</div>', unsafe_allow_html=True)
            else:
                selected_month_labels = st.multiselect(
                    "Custom Dates",
                    options=available_month_labels,
                    default=available_month_labels,
                    placeholder="Select one or more months"
                )

        with region_col:
            st.markdown("**Regions**")
            region_mode = st.radio(
                "Region Preset",
                options=["All", "UK", "North America", "DACH + BeNeLux", "Nordics", "ANZ", "Rest of Europe", "Rest of World", "Custom"],
                horizontal=True,
                label_visibility="collapsed"
            )

            if region_mode == "All":
                selected_regions = available_regions
                st.markdown('<div class="green-chip">All regions selected</div>', unsafe_allow_html=True)
            elif region_mode == "Custom":
                selected_regions = st.multiselect(
                    "Custom Regions",
                    options=available_regions,
                    default=available_regions,
                    placeholder="Select one or more regions"
                )
            else:
                selected_regions = [region_mode]
                st.markdown(f'<div class="green-chip">{region_mode} selected</div>', unsafe_allow_html=True)

        st.markdown("""
            <p class="small-note">
                Date and region filters are independent. Global grouping follows UK, North America, DACH + BeNeLux, Nordics, ANZ, Rest of Europe, and Rest of World.
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

        if selected_regions:
            filtered_geo = filtered_geo[filtered_geo["Region"].isin(selected_regions)].copy()
        else:
            filtered_geo = filtered_geo.iloc[0:0].copy()

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

        paid_analysis = build_paid_analysis(filtered_campaigns, filtered_keywords, filtered_geo)

        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Performance Analysis</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Overall Performance</div>
            <div class="insight-text">{bullets_to_html(paid_analysis["overall"])}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Areas for Optimization</div>
            <div class="insight-text">{bullets_to_html(paid_analysis["optimization"])}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Missed Opportunities</div>
            <div class="insight-text">{bullets_to_html(paid_analysis["opportunity"])}</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Campaign Summary</div>
        </div>
        """, unsafe_allow_html=True)

        campaign_section_analysis = build_campaign_section_analysis(filtered_campaigns)
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Campaign Insights</div>
            <div class="insight-text">{bullets_to_html(campaign_section_analysis)}</div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_campaigns.empty:
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
                height=430
            )
        else:
            st.info("No campaign summary data is available for the selected dates.")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Keyword Performance</div>
        </div>
        """, unsafe_allow_html=True)

        keyword_section_analysis = build_keyword_section_analysis(filtered_keywords)
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Keyword Insights</div>
            <div class="insight-text">{bullets_to_html(keyword_section_analysis)}</div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_keywords.empty:
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

            max_cpc_map = filtered_keywords.groupby("Keyword")["Max. CPC"].max().to_dict()
            keyword_table["Max. CPC"] = keyword_table["Keyword"].map(max_cpc_map)

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
                height=520
            )
        else:
            st.info("No enabled keyword data is available for the selected dates.")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div class="section-title">Global Performance</div>
        </div>
        """, unsafe_allow_html=True)

        global_section_analysis = build_global_section_analysis(filtered_geo, filtered_campaigns, filtered_keywords)
        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Global Insights</div>
            <div class="insight-text">{bullets_to_html(global_section_analysis)}</div>
        </div>
        """, unsafe_allow_html=True)

        if not filtered_geo.empty:
            geo_table = (
                filtered_geo.groupby(["Region", "Location"], as_index=False)[
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
                    "Region",
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
            ].sort_values(["Region", "Conversions", "Cost"], ascending=[True, False, False])

            st.dataframe(
                style_dataframe(geo_table),
                use_container_width=True,
                height=520
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
