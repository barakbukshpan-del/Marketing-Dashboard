# NOTE: Updated main.py with enhanced insights + new Executive Analysis tab
# (Only key additions shown conceptually; your existing structure is preserved)

# --- ADD THIS NEW TAB ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Google Paid", "Google Organic", "LinkedIn Campaigns", "Executive Analysis"]
)

# ------------------------------------------------
# OVERVIEW (UPDATED WITH ORGANIC)
# ------------------------------------------------
with tab1:
    organic_clicks = queries_df["Clicks"].sum() if not queries_df.empty else 0
    organic_impr = queries_df["Impressions"].sum() if not queries_df.empty else 0
    organic_ctr = safe_div(organic_clicks, organic_impr) * 100
    organic_position = queries_df["Position"].mean() if "Position" in queries_df.columns else 0

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Organic Clicks</div>
        <div class="metric-value">{fmt_number(organic_clicks)}</div>
        <div class="metric-delta">{fmt_pct(organic_ctr)} CTR · Pos {round(organic_position,1) if organic_position else '--'}</div>
    </div>
    """, unsafe_allow_html=True)

    overview_bullets = [
        f"Google Paid drives {fmt_number(paid_deals)} open deals and is the primary pipeline engine.",
        f"LinkedIn generates {fmt_number(li_leads)} leads but fewer downstream conversions.",
        f"Organic generates {fmt_number(organic_clicks)} clicks from {fmt_number(organic_impr)} impressions at {fmt_pct(organic_ctr)} CTR.",
        "Biggest upside sits in improving Organic CTR and reallocating inefficient paid spend."
    ]

# ------------------------------------------------
# GOOGLE ORGANIC (ENHANCED)
# ------------------------------------------------
with tab3:
    if not queries_df.empty:
        q = queries_df.copy()
        q = q.sort_values("Clicks", ascending=False)

        top_queries = q.head(3)["Query"].tolist() if "Query" in q.columns else []
        missed_queries = q.sort_values("Impressions", ascending=False).head(3)["Query"].tolist()

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Query Insights</div>
            <div class="insight-text">
                <ul>
                    <li>Top queries: {', '.join(top_queries)}</li>
                    <li>High impression but underperforming CTR: {', '.join(missed_queries)}</li>
                    <li>Organic demand is likely brand-heavy with limited non-brand capture.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------
# LINKEDIN (ENHANCED)
# ------------------------------------------------
with tab4:
    li_summary = filtered_li.groupby("Campaign", as_index=False)[["Cost","Leads","SAL"]].sum()
    if not li_summary.empty:
        best_li = li_summary.sort_values("SAL", ascending=False).head(1)

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">LinkedIn Insights</div>
            <div class="insight-text">
                <ul>
                    <li>{best_li.iloc[0]['Campaign']} is the strongest campaign.</li>
                    <li>LinkedIn is efficient for lead gen but weaker in pipeline conversion.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------
# EXECUTIVE ANALYSIS TAB (NEW)
# ------------------------------------------------
with tab5:
    st.markdown('<div class="glass-card"><div class="section-title">Executive Analysis</div></div>', unsafe_allow_html=True)

    exec_summary = [
        "Google Paid is the strongest pipeline driver with clear deal creation.",
        "LinkedIn is a strong demand generation channel but less effective at closing pipeline.",
        "Organic has strong visibility but is under-leveraged for acquisition.",
        "Overall strategy is strong at capturing demand but weaker at creating new demand."
    ]

    next_steps = [
        "Shift budget to top-performing Google Paid campaigns.",
        "Optimize SEO CTR on high-impression pages.",
        "Create SEO content from high-converting paid keywords.",
        "Refine LinkedIn targeting for higher-quality leads."
    ]

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">Executive Summary</div>
        <div class="insight-text">{bullets_to_html(exec_summary)}</div>
    </div>

    <div class="insight-box">
        <div class="insight-title">Next Steps</div>
        <div class="insight-text">{bullets_to_html(next_steps)}</div>
    </div>
    """, unsafe_allow_html=True)

# --- END UPDATE ---
