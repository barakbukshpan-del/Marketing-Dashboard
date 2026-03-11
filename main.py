import streamlit as st

st.set_page_config(
    page_title="Marketing Minisite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global app styling */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: white;
    }

    .stApp {
        background: linear-gradient(135deg, #031b3a 0%, #0a3d7a 45%, #1259b8 100%);
        color: white;
    }

    /* Main container spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1400px;
    }

    /* Headings and text */
    h1, h2, h3, h4, h5, h6, p, li, label, div, span {
        color: white !important;
    }

    /* Muted text helper */
    .muted {
        color: rgba(255, 255, 255, 0.78) !important;
    }

    /* Cards / sections */
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18);
    }

    /* Buttons */
    .stButton > button {
        background: white;
        color: #06264d;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1.2rem;
        font-weight: 700;
    }

    .stButton > button:hover {
        background: #e8f0ff;
        color: #031b3a;
    }

    /* Text input / text area / select styling */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.10) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.20) !important;
    }

    /* Tabs */
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

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.15);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* Hide Streamlit default header menu/footer */
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
            Your Marketing Headline Goes Here
        </h1>
        <p class="muted" style="font-size: 1.15rem; max-width: 850px;">
            This is the opening shell of your Streamlit minisite. The core design system is now set:
            dark blue gradient background, white text, and glass-style content containers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("Book a Demo"):
        st.toast("CTA placeholder clicked")

with col2:
    if st.button("Learn More"):
        st.toast("Secondary CTA placeholder clicked")

with col3:
    st.markdown(
        """
        <p class="muted" style="margin-top: 0.6rem;">
            We can now build each tab one by one with your content, messaging, and conversion flow.
        </p>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Solution", "Proof", "Contact"]
)

with tab1:
    st.markdown(
        """
        <div class="glass-card">
            <h2>Overview</h2>
            <p class="muted">
                This tab is ready for your top-level value proposition, summary copy, and intro messaging.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab2:
    st.markdown(
        """
        <div class="glass-card">
            <h2>Solution</h2>
            <p class="muted">
                This tab can hold product details, workflows, differentiators, and use cases.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab3:
    st.markdown(
        """
        <div class="glass-card">
            <h2>Proof</h2>
            <p class="muted">
                This tab can hold logos, testimonials, case studies, KPIs, or performance claims.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab4:
    st.markdown(
        """
        <div class="glass-card">
            <h2>Contact</h2>
            <p class="muted">
                This tab can become a lead form, demo request area, or booking section.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.success("Form submitted placeholder.")
