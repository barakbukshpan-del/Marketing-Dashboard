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

.stMultiSelect div[data-baseweb="tag"] {
    background: linear-gradient(135deg, #0b7a42 0%, #11a15a 100%) !important;
    color: white !important;
    border-radius: 10px !important;
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
    return f"{round(v, 1)}%"


def bullets_to_html(items):
    items = [x for x in items if x][:6]
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


def style_dataframe(df: pd.DataFrame):
    label_cols = {
        "Keyword", "Campaign", "Country", "Region", "Query", "Page",
        "Device", "Search appearance", "Month"
    }
    format_map = {}
    for c in df.columns:
        if c in label_cols:
            continue
        lower = c.lower()
        if "%" in c or "ctr" in lower or "rate" in lower or "position" in lower:
            format_map[c] = lambda x: "--" if pd.isna(x) else (f"{round(pd.to_numeric(x, errors='coerce'), 1)}" if pd.notna(pd.to_numeric(x, errors='coerce')) else str(x))
        elif "cost" in lower or "cpc" in lower or "cpl" in lower or "cpa" in lower:
            format_map[c] = lambda x: "--" if pd.isna(x) else (f"${round(pd.to_numeric(x, errors='coerce')):,}" if pd.notna(pd.to_numeric(x, errors='coerce')) else str(x))
        else:
            format_map[c] = lambda x: "--" if pd.isna(x) else (f"{round(pd.to_numeric(x, errors='coerce')):,}" if pd.notna(pd.to_numeric(x, errors='coerce')) else str(x))
    return df.style.format(format_map)


def build_google_campaign_rows(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy().iloc[:, :13]
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
        rows.append({
            "Month": f"{current_month_name}-{str(current_year)[-2:]}",
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
        })
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
        rows.append({
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
        })
    return pd.DataFrame(rows)


def first_col(df, preferred):
    for c in preferred:
        if c in df.columns:
            return c
    return df.columns[0] if len(df.columns) else None


def organic_insights_queries(df: pd.DataFrame):
    if df.empty:
        return ["No query data available."]
    query_col = first_col(df, ["Query", "Top queries", "Queries"])
    top_q = df.sort_values("Clicks", ascending=False).head(3)[query_col].astype(str).tolist() if query_col else []
    missed = df[(df["Impressions"] > df["Impressions"].median()) & (df["CTR"] < df["CTR"].median())]
    missed_q = missed.sort_values("Impressions", ascending=False).head(3)[query_col].astype(str).tolist() if query_col and not missed.empty else []
    brand_share_note = "Organic demand appears brand-heavy." if query_col and any("quick" in q.lower() for q in top_q) else "Organic demand has a mix of brand and non-brand queries."
    return [
        f"Top queries by clicks are {', '.join(top_q)}." if top_q else None,
        f"Highest-visibility low-CTR queries are {', '.join(missed_q)}." if missed_q else "There are no standout low-CTR query outliers in the current view.",
        brand_share_note,
        "Best SEO upside sits in improving CTR and ranking on already-visible query themes.",
    ]


def organic_insights_pages(df: pd.DataFrame):
    if df.empty:
        return ["No page data available."]
    page_col = first_col(df, ["Page", "Top pages", "Pages"])
    top_pages = df.sort_values("Clicks", ascending=False).head(3)[page_col].astype(str).tolist() if page_col else []
    weak_pages = df[(df["Impressions"] > df["Impressions"].median()) & (df["CTR"] < df["CTR"].median())]
    weak_pages = weak_pages.sort_values("Impressions", ascending=False).head(3)[page_col].astype(str).tolist() if page_col and not weak_pages.empty else []
    return [
        f"Top pages by clicks are {', '.join(top_pages)}." if top_pages else None,
        f"High-impression, low-CTR pages are {', '.join(weak_pages)}." if weak_pages else "No major page CTR underperformers stand out in the current view.",
        "Pages already ranking but not earning clicks should be optimized before creating net-new content.",
    ]


def organic_insights_countries(df: pd.DataFrame):
    if df.empty:
        return ["No country data available."]
    col = first_col(df, ["Country", "Countries"])
    top_c = df.sort_values("Clicks", ascending=False).head(3)[col].astype(str).tolist() if col else []
    best_ctr = df.sort_values("CTR", ascending=False).head(3)[col].astype(str).tolist() if col else []
    return [
        f"Top countries by organic clicks are {', '.join(top_c)}." if top_c else None,
        f"Strongest CTR markets are {', '.join(best_ctr)}." if best_ctr else None,
        "Countries performing well in both Organic and Paid should become priority growth markets.",
    ]


def organic_insights_devices(df: pd.DataFrame):
    if df.empty:
        return ["No device data available."]
    col = first_col(df, ["Device", "Devices"])
    best = df.sort_values("Clicks", ascending=False).head(1)
    weak_ctr = df.sort_values("CTR", ascending=True).head(1)
    return [
        f"{best.iloc[0][col]} is the strongest device by click volume." if col and not best.empty else None,
        f"{weak_ctr.iloc[0][col]} shows the weakest CTR and may point to UX or SERP-message issues." if col and not weak_ctr.empty else None,
        "Device performance should guide both landing-page UX priorities and metadata testing.",
    ]


def build_paid_analysis(campaign_df: pd.DataFrame, keyword_df: pd.DataFrame, geo_df: pd.DataFrame):
    bullets = {"overall": [], "optimization": [], "opportunity": []}
    if not campaign_df.empty:
        spend = campaign_df["Cost"].sum()
        clicks = campaign_df["Clicks"].sum()
        impr = campaign_df["Impr."].sum()
        hs_leads = campaign_df["HS leads"].sum()
        sal = campaign_df["SAL"].sum()
        deals = campaign_df["Open deal"].sum()
        bullets["overall"] += [
            f"{fmt_money(spend)} spend drove {fmt_number(clicks)} clicks, {fmt_number(hs_leads)} HS leads, {fmt_number(sal)} SALs, and {fmt_number(deals)} open deals.",
            f"Blended CTR is {fmt_pct(safe_div(clicks, impr) * 100)}, CPL is {fmt_money(safe_div(spend, hs_leads))}, and cost per SAL is {fmt_money(safe_div(spend, sal))}.",
        ]
        campaign_rank = campaign_df.groupby("Campaign", as_index=False)[["Cost", "Clicks", "Impr.", "HS leads", "SAL", "Open deal"]].sum()
        campaign_rank["CTR %"] = campaign_rank.apply(lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1)
        best = campaign_rank.sort_values(["Open deal", "SAL", "HS leads"], ascending=[False, False, False]).head(1)
        weak = campaign_rank[(campaign_rank["Cost"] > campaign_rank["Cost"].median()) & (campaign_rank["HS leads"] <= campaign_rank["HS leads"].median())].sort_values("Cost", ascending=False)
        leak = campaign_rank[(campaign_rank["HS leads"] > 0) & (campaign_rank["Open deal"] == 0)].sort_values(["HS leads", "SAL"], ascending=[False, False])
        opp = campaign_rank[(campaign_rank["HS leads"] > campaign_rank["HS leads"].median()) & (campaign_rank["CTR %"] < campaign_rank["CTR %"].median())]
        if not best.empty:
            bullets["overall"].append(f"{best.iloc[0]['Campaign']} is the strongest pipeline-driving campaign.")
        if not weak.empty:
            bullets["optimization"].append(f"Biggest efficiency pressure sits in {', '.join(weak['Campaign'].head(3).tolist())}.")
        if not leak.empty:
            bullets["optimization"].append(f"Lead-to-pipeline leakage is most visible in {', '.join(leak['Campaign'].head(3).tolist())}.")
        if not opp.empty:
            bullets["opportunity"].append(f"Best scale candidates are {', '.join(opp['Campaign'].head(3).tolist())} if click capture improves.")
    if not keyword_df.empty:
        kw = keyword_df.groupby("Keyword", as_index=False)[["Cost", "Clicks", "Impressions", "Conversions"]].sum()
        kw["CTR %"] = kw.apply(lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1)
        kw["Conv Rate %"] = kw.apply(lambda r: safe_div(r["Conversions"], r["Clicks"]) * 100, axis=1)
        best_kw = kw.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
        weak_kw = kw[(kw["Cost"] > kw["Cost"].median()) & (kw["Conversions"] <= kw["Conversions"].median())].sort_values("Cost", ascending=False).head(3)
        if not best_kw.empty:
            bullets["overall"].append(f"Top converting keywords are {', '.join(best_kw['Keyword'].tolist())}.")
        if not weak_kw.empty:
            bullets["optimization"].append(f"Spend-heavy keyword drag sits in {', '.join(weak_kw['Keyword'].tolist())}.")
        bullets["opportunity"].append("Paid-converting keyword themes should be promoted into SEO landing pages and content clusters.")
    if not geo_df.empty:
        geo = geo_df.groupby("Location", as_index=False)[["Cost", "Interactions", "Impr.", "Conversions"]].sum()
        geo["Conv Rate %"] = geo.apply(lambda r: safe_div(r["Conversions"], r["Interactions"]) * 100, axis=1)
        best_geo = geo.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
        weak_geo = geo[(geo["Cost"] > geo["Cost"].median()) & (geo["Conversions"] <= geo["Conversions"].median())].sort_values("Cost", ascending=False).head(3)
        if not best_geo.empty:
            bullets["overall"].append(f"Top GEO contributors are {', '.join(best_geo['Location'].tolist())}.")
        if not weak_geo.empty:
            bullets["optimization"].append(f"Weakest GEO efficiency shows up in {', '.join(weak_geo['Location'].tolist())}.")
    for key in bullets:
        if not bullets[key]:
            bullets[key] = ["No strong pattern stands out in the current filtered view."]
    return bullets


def build_campaign_section_analysis(campaign_df: pd.DataFrame):
    if campaign_df.empty:
        return ["No campaign-level data is available for the selected filters."]
    summary = campaign_df.groupby("Campaign", as_index=False)[["Cost", "Clicks", "Impr.", "HS leads", "SAL", "Open deal"]].sum()
    top_spend = summary.sort_values("Cost", ascending=False).head(1)
    top_pipeline = summary.sort_values(["Open deal", "SAL", "HS leads"], ascending=[False, False, False]).head(1)
    weak_eff = summary[(summary["Cost"] > summary["Cost"].median()) & (summary["HS leads"] <= summary["HS leads"].median())].sort_values("Cost", ascending=False).head(3)
    bullets = []
    if not top_spend.empty:
        bullets.append(f"Top spend campaign is {top_spend.iloc[0]['Campaign']} at {fmt_money(top_spend.iloc[0]['Cost'])}.")
    if not top_pipeline.empty:
        bullets.append(f"Strongest downstream pipeline campaign is {top_pipeline.iloc[0]['Campaign']}.")
    if not weak_eff.empty:
        bullets.append(f"Budget pressure is concentrated in {', '.join(weak_eff['Campaign'].tolist())}.")
    return bullets


def build_keyword_section_analysis(keyword_df: pd.DataFrame):
    if keyword_df.empty:
        return ["No keyword-level data is available for the selected filters."]
    kw = keyword_df.groupby("Keyword", as_index=False)[["Cost", "Clicks", "Impressions", "Conversions"]].sum()
    kw["CTR %"] = kw.apply(lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1)
    kw["Conv Rate %"] = kw.apply(lambda r: safe_div(r["Conversions"], r["Clicks"]) * 100, axis=1)
    top_conv = kw.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
    costly_kw = kw[(kw["Cost"] > kw["Cost"].median()) & (kw["Conversions"] <= kw["Conversions"].median())].sort_values("Cost", ascending=False).head(3)
    missed = kw[(kw["Impressions"] > kw["Impressions"].median()) & (kw["CTR %"] < kw["CTR %"].median())].sort_values("Impressions", ascending=False).head(3)
    bullets = []
    if not top_conv.empty:
        bullets.append(f"Top keyword performers are {', '.join(top_conv['Keyword'].tolist())}.")
    if not costly_kw.empty:
        bullets.append(f"Efficiency drag sits in {', '.join(costly_kw['Keyword'].tolist())}.")
    if not missed.empty:
        bullets.append(f"Best missed click opportunity is {', '.join(missed['Keyword'].tolist())}.")
    return bullets


def build_global_section_analysis(geo_df: pd.DataFrame):
    if geo_df.empty:
        return ["No global country-level data is available for the selected filters."]
    geo = geo_df.groupby(["Region", "Location"], as_index=False)[["Cost", "Interactions", "Impr.", "Conversions"]].sum()
    geo["Conv Rate %"] = geo.apply(lambda r: safe_div(r["Conversions"], r["Interactions"]) * 100, axis=1)
    top_country = geo.sort_values(["Conversions", "Conv Rate %"], ascending=[False, False]).head(3)
    weak_country = geo[(geo["Cost"] > geo["Cost"].median()) & (geo["Conversions"] <= geo["Conversions"].median())].sort_values("Cost", ascending=False).head(3)
    region_rollup = geo.groupby("Region", as_index=False)[["Cost", "Conversions"]].sum()
    region_rollup["Cost / Conv."] = region_rollup.apply(lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1)
    best_region = region_rollup.sort_values(["Conversions", "Cost / Conv."], ascending=[False, True]).head(1)
    bullets = []
    if not top_country.empty:
        bullets.append(f"Top country contributors are {', '.join(top_country['Location'].tolist())}.")
    if not weak_country.empty:
        bullets.append(f"Weakest country efficiency shows up in {', '.join(weak_country['Location'].tolist())}.")
    if not best_region.empty:
        bullets.append(f"{best_region.iloc[0]['Region']} is the strongest regional pocket.")
    return bullets


def build_linkedin_analysis(df: pd.DataFrame):
    bullets = {"overall": [], "optimization": [], "opportunity": []}
    if df.empty:
        return {k: ["No LinkedIn data is available for the selected filters."] for k in bullets}
    spend = df["Cost"].sum()
    clicks = df["Clicks"].sum()
    impr = df["Impr."].sum()
    leads = df["Leads"].sum()
    sal = df["SAL"].sum()
    open_deals = df["Open deal"].sum() if "Open deal" in df.columns else 0
    bullets["overall"] += [
        f"LinkedIn delivered {fmt_money(spend)} in spend, {fmt_number(clicks)} clicks, {fmt_number(leads)} leads, and {fmt_number(sal)} SALs.",
        f"CTR is {fmt_pct(safe_div(clicks, impr) * 100)}, CPL is {fmt_money(safe_div(spend, leads))}, and cost per SAL is {fmt_money(safe_div(spend, sal))}.",
    ]
    if open_deals > 0:
        bullets["overall"].append(f"LinkedIn also generated {fmt_number(open_deals)} open deals.")
    summary = df.groupby("Campaign", as_index=False)[["Cost", "Clicks", "Impr.", "Leads", "SAL", "Open deal"]].sum()
    best = summary.sort_values(["SAL", "Leads", "Open deal", "Cost"], ascending=[False, False, False, False]).head(1)
    weak = summary[(summary["Cost"] > summary["Cost"].median()) & (summary["Leads"] <= summary["Leads"].median())].sort_values("Cost", ascending=False).head(3)
    scale = summary[(summary["Leads"] > summary["Leads"].median()) & (summary["Cost"] < summary["Cost"].median())].sort_values("Leads", ascending=False).head(3)
    if not best.empty:
        bullets["overall"].append(f"Strongest LinkedIn campaign is {best.iloc[0]['Campaign']}.")
    if not weak.empty:
        bullets["optimization"].append(f"Spend efficiency pressure is concentrated in {', '.join(weak['Campaign'].tolist())}.")
    if not scale.empty:
        bullets["opportunity"].append(f"Best LinkedIn scale candidates are {', '.join(scale['Campaign'].tolist())}.")
    return bullets


# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data
def load_data():
    return {
        "keywords_df": pd.read_csv(Path("data/Google Paid Keywords.csv")),
        "geo_df": pd.read_csv(Path("data/Google Paid Locations.csv")),
        "campaign_raw_df": pd.read_csv(Path("data/Google Paid Campaigns.csv"), header=None),
        "linkedin_raw_df": pd.read_csv(Path("data/Linkedin Monthly Performance.csv"), header=None),
        "queries_df": pd.read_csv(Path("data/Queries.csv")),
        "pages_df": pd.read_csv(Path("data/Pages.csv")),
        "countries_df": pd.read_csv(Path("data/Countries.csv")),
        "devices_df": pd.read_csv(Path("data/Devices.csv")),
        "search_appearance_df": pd.read_csv(Path("data/Search appearance.csv")),
        "chart_df": pd.read_csv(Path("data/Chart.csv")),
        "filters_df": pd.read_csv(Path("data/Filters.csv")),
    }


data_loaded = True
load_error = None
try:
    data = load_data()
except Exception as e:
    data_loaded = False
    load_error = str(e)
    data = {}

keywords_df = data.get("keywords_df", pd.DataFrame())
geo_df = data.get("geo_df", pd.DataFrame())
campaign_raw_df = data.get("campaign_raw_df", pd.DataFrame())
linkedin_raw_df = data.get("linkedin_raw_df", pd.DataFrame())
queries_df = data.get("queries_df", pd.DataFrame())
pages_df = data.get("pages_df", pd.DataFrame())
countries_df = data.get("countries_df", pd.DataFrame())
devices_df = data.get("devices_df", pd.DataFrame())
search_appearance_df = data.get("search_appearance_df", pd.DataFrame())
chart_df = data.get("chart_df", pd.DataFrame())
filters_df = data.get("filters_df", pd.DataFrame())


# ------------------------------------------------
# CLEAN DATA
# ------------------------------------------------

if data_loaded:
    for organic_df, dim_name in [
        (queries_df, "Query"),
        (pages_df, "Page"),
        (countries_df, "Country"),
        (devices_df, "Device"),
        (search_appearance_df, "Search appearance"),
    ]:
        organic_df.columns = [str(c).strip() for c in organic_df.columns]
        for col in ["Clicks", "Impressions", "CTR", "Position"]:
            if col in organic_df.columns:
                organic_df[col] = clean_numeric(organic_df[col])
        if dim_name in organic_df.columns:
            organic_df[dim_name] = organic_df[dim_name].astype(str).str.strip()

    if not chart_df.empty:
        chart_df.columns = [str(c).strip() for c in chart_df.columns]
        for col in chart_df.columns:
            if str(col).lower() != "date":
                chart_df[col] = clean_numeric(chart_df[col])

    keywords_df["Month_dt"] = parse_month(keywords_df["Month"])
    keywords_df["Keyword"] = keywords_df["Keyword"].astype(str).str.strip().str.replace('"', "", regex=False)
    keywords_df["Keyword status"] = keywords_df["Keyword status"].astype(str).str.strip()
    for col in ["Cost", "Clicks", "Impressions", "Conversions", "Avg. CPC", "Max. CPC", "Cost / conv.", "Interactions", "Interaction rate", "Conv. rate", "Avg. cost"]:
        if col in keywords_df.columns:
            keywords_df[col] = clean_numeric(keywords_df[col])
    enabled_keywords = keywords_df[keywords_df["Keyword status"].str.lower() == "enabled"].copy()

    geo_df["Month_dt"] = parse_month(geo_df["Month"])
    geo_df["Location"] = geo_df["Location"].astype(str).str.strip()
    if "Campaign" in geo_df.columns:
        geo_df["Campaign"] = geo_df["Campaign"].astype(str).str.strip()
    for col in ["Cost", "Conversions", "Interactions", "Impr.", "Interaction rate", "Conv. rate", "Avg. cost", "Cost / conv."]:
        if col in geo_df.columns:
            geo_df[col] = clean_numeric(geo_df[col])
    geo_df = geo_df[geo_df["Location"].apply(is_valid_country)].copy()
    geo_df["Region"] = geo_df["Location"].apply(map_geo_region)

    campaigns_df = build_google_campaign_rows(campaign_raw_df)
    if not campaigns_df.empty:
        campaigns_df["Month_dt"] = parse_month(campaigns_df["Month"])
        campaigns_df["Campaign"] = campaigns_df["Campaign"].astype(str).str.strip()
        for col in ["Cost", "Impr.", "Clicks", "CTR", "Avg. CPC", "HS leads", "CPL", "SAL", "Open deal", "Cost per SAL"]:
            campaigns_df[col] = clean_numeric(campaigns_df[col])
    else:
        campaigns_df = pd.DataFrame(columns=["Month", "Campaign", "Cost", "Impr.", "Clicks", "CTR", "Avg. CPC", "HS leads", "CPL", "SAL", "Open deal", "Cost per SAL", "Month_dt"])

    linkedin_df = build_linkedin_rows(linkedin_raw_df)
    if not linkedin_df.empty:
        linkedin_df["Month_dt"] = parse_month(linkedin_df["Month"])
        linkedin_df["Campaign"] = linkedin_df["Campaign"].astype(str).str.strip()
        for col in ["Impr.", "Clicks", "CTR", "Cost", "Avg. CPC", "Leads", "CPL", "SAL", "Open deal", "Cost per SAL"]:
            linkedin_df[col] = clean_numeric(linkedin_df[col])
    else:
        linkedin_df = pd.DataFrame(columns=["Month", "Campaign", "Cost", "Impr.", "Clicks", "Leads", "CTR", "Avg. CPC", "CPL", "SAL", "Open deal", "Cost per SAL", "Month_dt"])

    available_months = sorted(pd.concat([
        enabled_keywords["Month_dt"].dropna(),
        geo_df["Month_dt"].dropna(),
        campaigns_df["Month_dt"].dropna(),
        linkedin_df["Month_dt"].dropna(),
    ]).unique()) if (not enabled_keywords.empty or not geo_df.empty or not campaigns_df.empty or not linkedin_df.empty) else []

    available_month_labels = [pd.Timestamp(m).strftime("%b %Y") for m in available_months]
    month_label_to_value = {pd.Timestamp(m).strftime("%b %Y"): pd.Timestamp(m) for m in available_months}
    q4_2025_labels = [label for label in available_month_labels if label in ["Oct 2025", "Nov 2025", "Dec 2025"]]
    q1_2026_labels = [label for label in available_month_labels if label in ["Jan 2026", "Feb 2026", "Mar 2026"]]
    available_regions = ["UK", "North America", "DACH + BeNeLux", "Nordics", "ANZ", "Rest of Europe", "Rest of World"]
else:
    enabled_keywords = pd.DataFrame()
    campaigns_df = pd.DataFrame()
    linkedin_df = pd.DataFrame()
    available_month_labels = []
    month_label_to_value = {}
    q4_2025_labels = []
    q1_2026_labels = []
    available_regions = []

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown(
    """
<div class="glass-card">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🦎 Quicklizard Marketing Dashboard</h1>
    <p style="font-size: 1.1rem; color: rgba(255,255,255,0.82) !important; margin-bottom: 0;">
        Q4–Q1 2026 Marketing Overview for Google Paid, Google Organic, and LinkedIn Campaigns
    </p>
</div>
""",
    unsafe_allow_html=True,
)

if load_error:
    st.error(f"Data load failed: {load_error}")

st.markdown("<hr>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Google Paid", "Google Organic", "LinkedIn Campaigns", "Executive Analysis"
])

# ------------------------------------------------
# OVERVIEW
# ------------------------------------------------

with tab1:
    paid_spend = campaigns_df["Cost"].sum() if not campaigns_df.empty else 0
    paid_clicks = campaigns_df["Clicks"].sum() if not campaigns_df.empty else 0
    paid_leads = campaigns_df["HS leads"].sum() if not campaigns_df.empty else 0
    paid_sal = campaigns_df["SAL"].sum() if not campaigns_df.empty else 0
    paid_deals = campaigns_df["Open deal"].sum() if not campaigns_df.empty else 0

    li_spend = linkedin_df["Cost"].sum() if not linkedin_df.empty else 0
    li_clicks = linkedin_df["Clicks"].sum() if not linkedin_df.empty else 0
    li_leads = linkedin_df["Leads"].sum() if not linkedin_df.empty else 0
    li_sal = linkedin_df["SAL"].sum() if not linkedin_df.empty else 0
    li_deals = linkedin_df["Open deal"].sum() if not linkedin_df.empty else 0

    organic_clicks = queries_df["Clicks"].sum() if not queries_df.empty else 0
    organic_impr = queries_df["Impressions"].sum() if not queries_df.empty else 0
    organic_ctr = safe_div(organic_clicks, organic_impr) * 100
    organic_position = queries_df["Position"].mean() if not queries_df.empty and "Position" in queries_df.columns else None

    st.markdown('<div class="glass-card"><div class="section-title">Cross-Channel KPI Snapshot</div></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    items = [
        ("Google Paid Spend", fmt_money(paid_spend), f"{fmt_number(paid_leads)} HS Leads · {fmt_number(paid_deals)} Open Deals"),
        ("LinkedIn Spend", fmt_money(li_spend), f"{fmt_number(li_leads)} Leads · {fmt_number(li_sal)} SALs"),
        ("Organic Clicks", fmt_number(organic_clicks), f"{fmt_number(organic_impr)} Impressions"),
        ("Organic CTR", fmt_pct(organic_ctr), f"Avg Position {round(organic_position, 1) if organic_position is not None and pd.notna(organic_position) else '--'}"),
        ("Paid vs Organic", fmt_number(paid_clicks + li_clicks), f"Paid clicks vs {fmt_number(organic_clicks)} Organic clicks"),
    ]
    for col, (label, value, delta) in zip(cols, items):
        with col:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-delta">{delta}</div></div>''', unsafe_allow_html=True)

    overview_bullets = [
        f"Google Paid is the primary pipeline engine with {fmt_number(paid_deals)} open deals and {fmt_number(paid_leads)} HS leads.",
        f"LinkedIn is creating demand with {fmt_number(li_leads)} leads and {fmt_number(li_sal)} SALs, but downstream pipeline is lighter than Google Paid.",
        f"Organic generated {fmt_number(organic_clicks)} clicks from {fmt_number(organic_impr)} impressions at {fmt_pct(organic_ctr)} CTR.",
        f"Average organic position of {round(organic_position, 1) if organic_position is not None and pd.notna(organic_position) else '--'} suggests visibility exists, but ranking strength can improve.",
        "Biggest upside is improving organic CTR on already-visible queries/pages and reallocating paid spend from weaker campaigns into proven pipeline drivers.",
    ]
    st.markdown(f'''<div class="insight-box"><div class="insight-title">Overview Insights</div><div class="insight-text">{bullets_to_html(overview_bullets)}</div></div>''', unsafe_allow_html=True)

    summary_rows = pd.DataFrame([
        {"Channel": "Google Paid", "Spend": paid_spend, "Clicks": paid_clicks, "Leads": paid_leads, "SAL": paid_sal, "Open Deals": paid_deals, "CTR": safe_div(paid_clicks, campaigns_df["Impr."].sum()) * 100 if not campaigns_df.empty else 0, "Efficiency": safe_div(paid_spend, paid_leads)},
        {"Channel": "LinkedIn", "Spend": li_spend, "Clicks": li_clicks, "Leads": li_leads, "SAL": li_sal, "Open Deals": li_deals, "CTR": safe_div(li_clicks, linkedin_df["Impr."].sum()) * 100 if not linkedin_df.empty else 0, "Efficiency": safe_div(li_spend, li_leads)},
        {"Channel": "Organic", "Spend": 0, "Clicks": organic_clicks, "Leads": None, "SAL": None, "Open Deals": None, "CTR": organic_ctr, "Efficiency": organic_position if organic_position is not None else None},
    ])
    st.dataframe(style_dataframe(summary_rows.rename(columns={"Efficiency": "Key Metric"})), use_container_width=True, height=220)

# ------------------------------------------------
# GOOGLE PAID
# ------------------------------------------------

with tab2:
    if campaigns_df.empty and enabled_keywords.empty:
        st.error("Google Paid data files were not found or could not be parsed.")
    else:
        st.markdown('<div class="glass-card"><div class="section-title">Filters</div></div>', unsafe_allow_html=True)
        date_col, region_col = st.columns(2)
        with date_col:
            date_mode = st.radio("Date Preset", ["All", "Q4 2025", "Q1 2026", "Custom"], horizontal=True, label_visibility="collapsed", key="gp_date_mode")
            if date_mode == "All":
                selected_month_labels = available_month_labels
            elif date_mode == "Q4 2025":
                selected_month_labels = q4_2025_labels
            elif date_mode == "Q1 2026":
                selected_month_labels = q1_2026_labels
            else:
                selected_month_labels = st.multiselect("Custom Dates", options=available_month_labels, default=available_month_labels, key="gp_custom_dates")
        with region_col:
            region_mode = st.radio("Region Preset", ["All", "UK", "North America", "DACH + BeNeLux", "Nordics", "ANZ", "Rest of Europe", "Rest of World", "Custom"], horizontal=True, label_visibility="collapsed", key="gp_region_mode")
            if region_mode == "All":
                selected_regions = available_regions
            elif region_mode == "Custom":
                selected_regions = st.multiselect("Custom Regions", options=available_regions, default=available_regions, key="gp_custom_regions")
            else:
                selected_regions = [region_mode]

        selected_month_values = [month_label_to_value[label] for label in selected_month_labels if label in month_label_to_value]
        filtered_keywords = enabled_keywords[enabled_keywords["Month_dt"].isin(selected_month_values)].copy() if selected_month_values else enabled_keywords.iloc[0:0].copy()
        filtered_geo = geo_df[geo_df["Month_dt"].isin(selected_month_values)].copy() if selected_month_values else geo_df.iloc[0:0].copy()
        filtered_campaigns = campaigns_df[campaigns_df["Month_dt"].isin(selected_month_values)].copy() if selected_month_values else campaigns_df.iloc[0:0].copy()
        if selected_regions:
            filtered_geo = filtered_geo[filtered_geo["Region"].isin(selected_regions)].copy()

        total_spend = filtered_campaigns["Cost"].sum() if not filtered_campaigns.empty else filtered_keywords["Cost"].sum()
        total_clicks = filtered_campaigns["Clicks"].sum() if not filtered_campaigns.empty else filtered_keywords["Clicks"].sum()
        total_hs_leads = filtered_campaigns["HS leads"].sum() if not filtered_campaigns.empty else 0
        total_open_deals = filtered_campaigns["Open deal"].sum() if not filtered_campaigns.empty else 0
        cols = st.columns(4)
        for col, label, value, delta in [
            (cols[0], "Total Spend", fmt_money(total_spend), "Across selected dates"),
            (cols[1], "Total Clicks", fmt_number(total_clicks), "Paid search clicks"),
            (cols[2], "HS Leads", fmt_number(total_hs_leads), "Campaign outcome"),
            (cols[3], "Open Deals", fmt_number(total_open_deals), "Pipeline signal"),
        ]:
            with col:
                st.markdown(f'''<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-delta">{delta}</div></div>''', unsafe_allow_html=True)

        paid_analysis = build_paid_analysis(filtered_campaigns, filtered_keywords, filtered_geo)
        st.markdown('<div class="glass-card"><div class="section-title">Performance Analysis</div></div>', unsafe_allow_html=True)
        for title, key in [("Overall Performance", "overall"), ("Areas for Optimization", "optimization"), ("Missed Opportunities", "opportunity")]:
            st.markdown(f'''<div class="insight-box"><div class="insight-title">{title}</div><div class="insight-text">{bullets_to_html(paid_analysis[key])}</div></div>''', unsafe_allow_html=True)

        st.markdown('<div class="glass-card"><div class="section-title">Campaign Summary</div></div>', unsafe_allow_html=True)
        st.markdown(f'''<div class="insight-box"><div class="insight-title">Campaign Insights</div><div class="insight-text">{bullets_to_html(build_campaign_section_analysis(filtered_campaigns))}</div></div>''', unsafe_allow_html=True)
        if not filtered_campaigns.empty:
            campaign_table = filtered_campaigns.groupby("Campaign", as_index=False)[["Impr.", "Clicks", "Cost", "HS leads", "SAL", "Open deal"]].sum()
            campaign_table["CTR %"] = campaign_table.apply(lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1)
            campaign_table["Avg. CPC"] = campaign_table.apply(lambda r: safe_div(r["Cost"], r["Clicks"]), axis=1)
            campaign_table["CPL"] = campaign_table.apply(lambda r: safe_div(r["Cost"], r["HS leads"]), axis=1)
            campaign_table["Cost per SAL"] = campaign_table.apply(lambda r: safe_div(r["Cost"], r["SAL"]), axis=1)
            st.dataframe(style_dataframe(campaign_table.sort_values(["HS leads", "Open deal", "Cost"], ascending=[False, False, False])), use_container_width=True, height=420)

        st.markdown('<div class="glass-card"><div class="section-title">Keyword Performance</div></div>', unsafe_allow_html=True)
        st.markdown(f'''<div class="insight-box"><div class="insight-title">Keyword Insights</div><div class="insight-text">{bullets_to_html(build_keyword_section_analysis(filtered_keywords))}</div></div>''', unsafe_allow_html=True)
        if not filtered_keywords.empty:
            keyword_table = filtered_keywords.groupby("Keyword", as_index=False)[["Interactions", "Clicks", "Impressions", "Cost", "Conversions"]].sum()
            keyword_table["CTR %"] = keyword_table.apply(lambda r: safe_div(r["Clicks"], r["Impressions"]) * 100, axis=1)
            keyword_table["Conv Rate %"] = keyword_table.apply(lambda r: safe_div(r["Conversions"], r["Clicks"]) * 100, axis=1)
            keyword_table["Avg. CPC"] = keyword_table.apply(lambda r: safe_div(r["Cost"], r["Clicks"]), axis=1)
            st.dataframe(style_dataframe(keyword_table.sort_values(["Conversions", "Cost"], ascending=[False, False])), use_container_width=True, height=500)

        st.markdown('<div class="glass-card"><div class="section-title">Global Performance</div></div>', unsafe_allow_html=True)
        st.markdown(f'''<div class="insight-box"><div class="insight-title">Global Insights</div><div class="insight-text">{bullets_to_html(build_global_section_analysis(filtered_geo))}</div></div>''', unsafe_allow_html=True)
        if not filtered_geo.empty:
            geo_table = filtered_geo.groupby(["Region", "Location"], as_index=False)[["Impr.", "Interactions", "Cost", "Conversions"]].sum().rename(columns={"Location": "Country"})
            geo_table["Interaction Rate %"] = geo_table.apply(lambda r: safe_div(r["Interactions"], r["Impr."]) * 100, axis=1)
            geo_table["Conv Rate %"] = geo_table.apply(lambda r: safe_div(r["Conversions"], r["Interactions"]) * 100, axis=1)
            geo_table["Avg. Cost"] = geo_table.apply(lambda r: safe_div(r["Cost"], r["Interactions"]), axis=1)
            geo_table["Cost / Conv."] = geo_table.apply(lambda r: safe_div(r["Cost"], r["Conversions"]), axis=1)
            st.dataframe(style_dataframe(geo_table.sort_values(["Region", "Conversions", "Cost"], ascending=[True, False, False])), use_container_width=True, height=500)

# ------------------------------------------------
# GOOGLE ORGANIC
# ------------------------------------------------

with tab3:
    if queries_df.empty and pages_df.empty:
        st.error("Organic data not loaded.")
    else:
        organic_clicks = queries_df["Clicks"].sum() if not queries_df.empty else 0
        organic_impr = queries_df["Impressions"].sum() if not queries_df.empty else 0
        organic_ctr = safe_div(organic_clicks, organic_impr) * 100
        organic_position = queries_df["Position"].mean() if "Position" in queries_df.columns and not queries_df.empty else None

        st.markdown('<div class="glass-card"><div class="section-title">Google Organic Performance</div></div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for col, label, value, delta in [
            (cols[0], "Total Clicks", fmt_number(organic_clicks), "Organic search clicks"),
            (cols[1], "Total Impressions", fmt_number(organic_impr), "Search visibility"),
            (cols[2], "Average CTR", fmt_pct(organic_ctr), "Search click capture"),
            (cols[3], "Average Position", "--" if organic_position is None or pd.isna(organic_position) else f"{round(organic_position,1)}", "Ranking strength"),
        ]:
            with col:
                st.markdown(f'''<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-delta">{delta}</div></div>''', unsafe_allow_html=True)

        st.markdown(f'''<div class="insight-box"><div class="insight-title">Query Insights</div><div class="insight-text">{bullets_to_html(organic_insights_queries(queries_df))}</div></div>''', unsafe_allow_html=True)
        if not queries_df.empty:
            q = queries_df.copy()
            st.dataframe(style_dataframe(q.sort_values("Clicks", ascending=False).head(20)), use_container_width=True, height=420)

        st.markdown(f'''<div class="insight-box"><div class="insight-title">Page Insights</div><div class="insight-text">{bullets_to_html(organic_insights_pages(pages_df))}</div></div>''', unsafe_allow_html=True)
        if not pages_df.empty:
            st.dataframe(style_dataframe(pages_df.sort_values("Clicks", ascending=False).head(20)), use_container_width=True, height=420)

        st.markdown(f'''<div class="insight-box"><div class="insight-title">Geo Insights</div><div class="insight-text">{bullets_to_html(organic_insights_countries(countries_df))}</div></div>''', unsafe_allow_html=True)
        if not countries_df.empty:
            st.dataframe(style_dataframe(countries_df.sort_values("Clicks", ascending=False).head(20)), use_container_width=True, height=380)

        st.markdown(f'''<div class="insight-box"><div class="insight-title">Device Insights</div><div class="insight-text">{bullets_to_html(organic_insights_devices(devices_df))}</div></div>''', unsafe_allow_html=True)
        if not devices_df.empty:
            st.dataframe(style_dataframe(devices_df.sort_values("Clicks", ascending=False)), use_container_width=True, height=220)

        if not search_appearance_df.empty:
            sa_col = first_col(search_appearance_df, ["Search appearance"])
            sa_top = search_appearance_df.sort_values("Clicks", ascending=False).head(3)[sa_col].astype(str).tolist() if sa_col else []
            st.markdown(f'''<div class="insight-box"><div class="insight-title">Search Appearance Insights</div><div class="insight-text">{bullets_to_html([f"Search appearance is strongest in {', '.join(sa_top)}." if sa_top else None, "Limited rich-result diversity may point to structured data opportunities."])}</div></div>''', unsafe_allow_html=True)
            st.dataframe(style_dataframe(search_appearance_df.sort_values("Clicks", ascending=False)), use_container_width=True, height=220)

        organic_final = [
            "SEO is currently stronger at capturing branded demand than non-brand category demand.",
            "Fastest win is CTR optimization on already-visible queries and pages.",
            "Highest medium-term upside is building landing pages around paid-proven keyword themes.",
            "Priority should go to pages and queries already ranking on page 1–2 before scaling content volume.",
        ]
        st.markdown(f'''<div class="glass-card"><div class="section-title">Strategic Organic Analysis & Next Steps</div><div class="insight-box"><div class="insight-text">{bullets_to_html(organic_final)}</div></div></div>''', unsafe_allow_html=True)

# ------------------------------------------------
# LINKEDIN CAMPAIGNS
# ------------------------------------------------

with tab4:
    if linkedin_df.empty:
        st.error("LinkedIn data file was not found or could not be parsed.")
    else:
        st.markdown('<div class="glass-card"><div class="section-title">Filters</div></div>', unsafe_allow_html=True)
        li_date_mode = st.radio("LinkedIn Date Preset", ["All", "Q4 2025", "Q1 2026", "Custom"], horizontal=True, label_visibility="collapsed", key="li_date_mode")
        if li_date_mode == "All":
            li_selected_month_labels = available_month_labels
        elif li_date_mode == "Q4 2025":
            li_selected_month_labels = q4_2025_labels
        elif li_date_mode == "Q1 2026":
            li_selected_month_labels = q1_2026_labels
        else:
            li_selected_month_labels = st.multiselect("LinkedIn Custom Dates", options=available_month_labels, default=available_month_labels, key="li_custom_dates")
        li_month_values = [month_label_to_value[label] for label in li_selected_month_labels if label in month_label_to_value]
        filtered_li = linkedin_df[linkedin_df["Month_dt"].isin(li_month_values)].copy() if li_month_values else linkedin_df.iloc[0:0].copy()

        li_spend = filtered_li["Cost"].sum()
        li_clicks = filtered_li["Clicks"].sum()
        li_leads = filtered_li["Leads"].sum()
        li_sal = filtered_li["SAL"].sum()
        li_open_deals = filtered_li["Open deal"].sum() if "Open deal" in filtered_li.columns else 0
        cols = st.columns(4)
        for col, label, value, delta in [
            (cols[0], "Total Spend", fmt_money(li_spend), "Across selected dates"),
            (cols[1], "Total Clicks", fmt_number(li_clicks), "LinkedIn clicks"),
            (cols[2], "Leads", fmt_number(li_leads), "Lead generation output"),
            (cols[3], "SAL", fmt_number(li_sal), f"{fmt_number(li_open_deals)} Open Deals"),
        ]:
            with col:
                st.markdown(f'''<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-delta">{delta}</div></div>''', unsafe_allow_html=True)

        li_analysis = build_linkedin_analysis(filtered_li)
        st.markdown('<div class="glass-card"><div class="section-title">Performance Analysis</div></div>', unsafe_allow_html=True)
        for title, key in [("Overall Performance", "overall"), ("Areas for Optimization", "optimization"), ("Missed Opportunities", "opportunity")]:
            st.markdown(f'''<div class="insight-box"><div class="insight-title">{title}</div><div class="insight-text">{bullets_to_html(li_analysis[key])}</div></div>''', unsafe_allow_html=True)

        if not filtered_li.empty:
            li_table = filtered_li.groupby("Campaign", as_index=False)[["Impr.", "Clicks", "Cost", "Leads", "SAL", "Open deal"]].sum()
            li_table["CTR %"] = li_table.apply(lambda r: safe_div(r["Clicks"], r["Impr."]) * 100, axis=1)
            li_table["Avg. CPC"] = li_table.apply(lambda r: safe_div(r["Cost"], r["Clicks"]), axis=1)
            li_table["CPL"] = li_table.apply(lambda r: safe_div(r["Cost"], r["Leads"]), axis=1)
            li_table["Cost per SAL"] = li_table.apply(lambda r: safe_div(r["Cost"], r["SAL"]), axis=1)
            st.markdown('<div class="glass-card"><div class="section-title">Campaign Summary</div></div>', unsafe_allow_html=True)
            st.dataframe(style_dataframe(li_table.sort_values(["SAL", "Leads", "Open deal", "Cost"], ascending=[False, False, False, False])), use_container_width=True, height=500)

# ------------------------------------------------
# EXECUTIVE ANALYSIS
# ------------------------------------------------

with tab5:
    st.markdown('<div class="glass-card"><div class="section-title">Executive Analysis</div></div>', unsafe_allow_html=True)
    paid_deals = campaigns_df["Open deal"].sum() if not campaigns_df.empty else 0
    li_sal_total = linkedin_df["SAL"].sum() if not linkedin_df.empty else 0
    organic_clicks = queries_df["Clicks"].sum() if not queries_df.empty else 0
    organic_pos = queries_df["Position"].mean() if not queries_df.empty and "Position" in queries_df.columns else None

    exec_summary = [
        f"Google Paid is currently the strongest direct pipeline channel with {fmt_number(paid_deals)} open deals.",
        f"LinkedIn is a strong demand-generation channel with {fmt_number(li_sal_total)} SALs, but its downstream pipeline signal is lighter than Paid Search.",
        f"Organic is generating {fmt_number(organic_clicks)} clicks, but average position of {round(organic_pos,1) if organic_pos is not None and pd.notna(organic_pos) else '--'} indicates more ranking upside remains.",
        "The business is stronger at capturing existing demand than creating non-brand category demand.",
    ]
    what_is_working = [
        "Google Paid campaigns are proving downstream pipeline value.",
        "LinkedIn is contributing scalable lead creation.",
        "Organic already captures meaningful search demand and brand validation.",
        "Some GEOs show strength across both paid and organic signals.",
    ]
    underperforming = [
        "Part of paid spend is tied up in campaigns and GEOs that do not convert into pipeline efficiently.",
        "Organic visibility is not translating into clicks strongly enough on some priority queries and pages.",
        "Non-brand discovery is still weaker than it needs to be for scalable acquisition.",
        "LinkedIn’s role in the funnel is clearer at lead creation than at opportunity creation.",
    ]
    cross_channel = [
        "Promote paid-converting keyword themes into SEO landing pages and content clusters.",
        "Use LinkedIn’s best-performing pain points to improve organic page messaging and paid ad copy.",
        "Prioritize SEO in GEOs that already show paid efficiency.",
        "Use Organic CTR learnings to improve SERP messaging and ad-copy testing.",
    ]
    next_30 = [
        "Reduce budget on inefficient paid campaigns and shift into proven pipeline drivers.",
        "Rewrite metadata for top high-impression, low-CTR organic pages and queries.",
        "Identify the top 20 non-brand queries to target with content or landing pages.",
    ]
    next_60 = [
        "Build 3–5 SEO landing pages around proven paid-intent themes.",
        "Tighten LinkedIn audience and offer segmentation.",
        "Align GEO priorities across Organic and Paid.",
    ]
    next_90 = [
        "Add pipeline and revenue attribution into the dashboard.",
        "Create a unified keyword strategy across Paid and Organic.",
        "Establish a monthly channel scorecard across Spend, Clicks, Leads, SALs, Deals, CTR, and Position.",
    ]

    sections = [
        ("Executive Summary", exec_summary),
        ("What Is Working", what_is_working),
        ("What Is Underperforming", underperforming),
        ("Cross-Channel Opportunities", cross_channel),
        ("Priority Actions: Next 30 Days", next_30),
        ("Priority Actions: Next 60 Days", next_60),
        ("Priority Actions: Next 90 Days", next_90),
    ]
    for title, bullets in sections:
        st.markdown(f'''<div class="insight-box"><div class="insight-title">{title}</div><div class="insight-text">{bullets_to_html(bullets)}</div></div>''', unsafe_allow_html=True)
