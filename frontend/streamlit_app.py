import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_BASE = "" # My Kubernetes external URL

st.set_page_config(page_title="Macro Insights Dashboard",
                   page_icon="📊",
                   layout="wide")

st.title("📊 macro Insights - Economic Dashboard")


# ---------------------------
# Helper for API calls
# ---------------------------

def get_data(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None
    


# ---------------------------
# Sidebar navigation
# ---------------------------


menu = st.sidebar.radio(
    "Navigation",
    ["South Africa", "United States", "Tools"]
)


# ==================================
#       SOUTH AFRICA DASHBOARD
# ==================================

if menu == "South Africa":
    st.header("ZA South Africa Economic Indicators")

    tab1, tab2, tab3 = st.labs(["Inflation", "GDP Growth", "Interest Rates"])

    # Inflation
    with tab1:
        df = get_data("sa/inflation")
        if df is not None and not df.empty:
            st.subheader("South Africa Inflation (%)")
            st.line_chart(df.set_index("Date")["Value"])
        
        else:
            st.warning("No inflation data available.")

    # GDP Growth
    with tab2:
        df = get_data("sa/gdp")
        if df is not None and not df.empty:
            st.subheader("GDP Growth (%)")
            st.line_chart(df.set_index("Date")["value"])
        
        else:
            st.warning("No GDP Growth data available.")

    # Interest Rates
    with tab3:
        df = get_data("sa/rates")
        if df is not None and not df.empty:
            st.subheader("Repo / Lending Rate (%)")
            st.line_chart(df.set_index("Date")["Value"])
        
        else:
            st.warning("No rate data available.")


# =======================================
#           UNITED STATES DASHBOARD
# =======================================


if menu == "United States":
    st.header("US United States Economic Indicators")

    tab1, tab2, tab3 = st.labs(["Inflation", "GDP Growth", "Interest Rates"])

    # Inflation
    with tab1:
        df = get_data("us/inflation")
        if df is not None and not df.empty:
            st.subheader("US Inflation (%)")
            st.line_chart(df.set_index("Date")["Value"])

        else:
            st.warning("No inflation data available.")

    
    # GDP
    with tab2:
        df = get_data("us/gdp")
        if df is not None and not df.empty:
            st.subheader("US GDP Growth (%)")
            st.line_chart(df.set_index("Date")["Value"])

        else:
            st.warning("No GDP Growth data available.")


    # Rates
    with tab3:
        df = get_data("us/rates")
        if df is not None and not df.empty:
            st.subheader("US Lending Rate (%)")
            st.line_chart(df.set_index("Date")["Value"])

        else:
            st.warning("No interest rate data available.")


# ===========================================
#                   TOOLS
# ===========================================