import streamlit as st
import pandas as pd
import os

# --- 1. MANDATORY THEME CONFIG ---
st.set_page_config(page_title="Quicklizard Marketing Dashboard", layout="wide")

# CSS to force Deep Black Background and High-Contrast White Text
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #222222; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { color: #ffffff !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Campaign Square Styling */
    .campaign-container {
        border: 1px solid #ffffff;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 25px;
        background-color: #000000;
    }
    
    /* Table Visibility */
    .stDataFrame, div[data-testid="stTable"] { border: 1px solid #333333; background-color: #000000; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE PERMANENT HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://quicklizard.com/wp-content/uploads/2021/03/Quicklizard-Logo-1.png", width=180)
with col_title:
    st.markdown("<h1 style='margin-top: 10px;'>Quicklizard Marketing Dashboard</h1>", unsafe_allow_html=True)

# --- 3. TAB SELECTION & SUBHEADER ---
# We are building this one-by-one, starting with Google Paid Search
st.markdown("### Google Paid Search")
st.markdown("---")

# --- 4. DATA ENGINE ---
@st.cache_data
def load_and_clean(file, skip=0):
    if not os.path.exists(file): return pd.DataFrame()
    df = pd.read_csv(file, skiprows=skip)
    
    # Standard cleaning for numeric conversion
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(r'[%\$,]', '', regex=True).replace(['--', ' --'], '0')
            if any(char.isdigit() for char in str(df[col].iloc[0])):
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # HARD FILTER: Only show active data (Spend > 0 AND Impressions > 0)
    if 'Cost' in df.columns and 'Impr.' in df.columns:
        df = df[(df['Cost'] > 0) & (df['Impr.'] > 0)]
    return df

# Loading the two new CSVs you provided
df_keywords = load_and_clean("New Search Report Google Paid.csv", skip=2)
df_locations = load_and_clean("New Location Report Google Paid.csv", skip=2)

# --- 5. THE NARRATIVE ---
st.markdown("""
### Strategic Overview: Investing in Intent
Google Paid Search is our 'active acquisition engine.' Unlike other channels, this is where we pay to be at the top of the conversation when a potential client is searching for a solution to their pricing challenges. 

**The Active Portfolio Policy:** For this presentation, we have filtered out the 'noise.' The tables below only show keywords and locations where we actively deployed capital and where the market actually saw our ads. If a keyword has zero impressions or zero spend, it is excluded to ensure the Board stays focused on our active growth engines.
""")

# --- 6. CAMPAIGN SQUARES (NA, EMEA, TL) ---
st.markdown("---")
st.markdown("### Active Campaign Performance")

# Mapping your spreadsheet campaigns into the 3 requested squares
if not df_keywords.empty:
    col_na, col_emea, col_tl = st.columns(3)
    
    with col_na:
        st.markdown("#### North America (NA)")
        na_data = df_keywords[df_keywords['Campaign'].str.contains('NA|USA', case=False, na=False)]
        if not na_data.empty:
            na_cols = st.multiselect("Filter NA Columns", na_data.columns.tolist(), default=['Month', 'Keyword', 'Interactions', 'Cost'], key="na")
            st.dataframe(na_data[na_cols], use_container_width=True)
        else: st.write("No active NA data found.")

    with col_emea:
        st.markdown("#### Europe (EMEA)")
        emea_data = df_keywords[df_keywords['Campaign'].str.contains('Germany|EMEA|Moranne', case=False, na=False)]
        if not emea_data.empty:
            emea_cols = st.multiselect("Filter EMEA Columns", emea_data.columns.tolist(), default=['Month', 'Keyword', 'Interactions', 'Cost'], key="emea")
            st.dataframe(emea_data[emea_cols], use_container_width=True)
        else: st.write("No active EMEA data found.")

    with col_tl:
        st.markdown("#### Thought Leadership (TL)")
        tl_data = df_keywords[df_keywords['Campaign'].str.contains('TL|Thought', case=False, na=False)]
        if not tl_data.empty:
            tl_cols = st.multiselect("Filter TL Columns", tl_data.columns.tolist(), default=['Month', 'Keyword', 'Interactions', 'Cost'], key="tl")
            st.dataframe(tl_data[tl_cols], use_container_width=True)
        else: st.write("No active TL data found.")

# --- 7. GEOGRAPHIC PERFORMANCE ---
st.markdown("---")
st.markdown("### Strategic Geographic Deployment")
if not df_locations.empty:
    # Remove rows where Location is empty or a total summary
    clean_geo = df_locations[df_locations['Location'].notna()]
    st.dataframe(clean_geo[['Month', 'Location', 'Campaign', 'Impr.', 'Interactions', 'Cost']], use_container_width=True)
