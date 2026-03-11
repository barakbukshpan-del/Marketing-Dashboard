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
# HERO
# -----------------------------
st.markdown(
    """
    <div class="glass-card">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">
            🦎 Quicklizard Marketing Dashboard
        </h1>
        <p class="muted" style="font-size: 1.15rem; max-width: 850px;">
            This is an overview for the past 6 months for our main marketing Channels:
            Google SEO, Google Organic, Linkedin Campaigns
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
    ["Overview", "Google SEO", "Google Organic", "LinkedIn Campaigns"]
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

    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Overview Notes</div>
            <p class="muted">
                We can use this area for a short written summary of what happened across SEO, Organic, and LinkedIn Campaigns.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# GOOGLE SEO TAB
# -----------------------------
with tab2:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Google SEO</div>
            <p class="muted">
                This tab will focus on search performance, rankings, impressions, clicks, and organic search visibility.
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
                <div class="metric-label">SEO Clicks</div>
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
                <div class="metric-label">SEO Impressions</div>
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
                <div class="metric-label">Average Position</div>
                <div class="metric-value">--</div>
                <div class="metric-delta">Placeholder metric</div>
            </div>
            """,
            unsafe_allow_html=True,
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
