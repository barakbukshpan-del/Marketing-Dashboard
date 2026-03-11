# -----------------------------
# LOAD DATA
# -----------------------------
import pandas as pd

@st.cache_data
def load_google_paid_data():

    keywords_path = "data/Google Paid Keywords.csv"
    locations_path = "data/Google Paid Locations.csv"

    keywords_df = pd.read_csv(keywords_path)
    locations_df = pd.read_csv(locations_path)

    return keywords_df, locations_df


keywords_df, locations_df = load_google_paid_data()
