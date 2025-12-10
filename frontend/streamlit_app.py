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

    tab1, tab2, tab3 = st.tabs(["Inflation", "GDP Growth", "Interest Rates"])

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
            st.line_chart(df.set_index("Date")["Value"])
        
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

    tab1, tab2, tab3 = st.tabs(["Inflation", "GDP Growth", "Interest Rates"])

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

if menu == "Tools":
    st.header("🛠️ Tools & Calculators")

    tool = st.selectbox("Choose a tool:", ["🏪 Grocery Inflation", "🏦 Loan Calculator"])

    # Grocery inflation calculator
    if tool == "🏪 Grocery Inflation":
        st.subheader("Grocery Inflation Cost Estimator")

        amount = st.number_input("How much do you spend per month on groceries (R)❓", min_value=0)

        df = get_data("sa/inflation")

        if df is not None and not df.empty:
            latest = df["Value"].iloc[-1] / 100
            increased = amount * (1 + latest)
            st.write(f"Inflation-adjusted monthly cost: **R{increased:,.2f}**")
        else:
            st.warning("Inflation data unavailable.")

    # Loan Calculator
    if tool == "🏦 Loan Calculator":
        st.subheader("Loan Cost Calculator (based on repo rate)")

        loan = st.number_input("Loan Amount (R)", min_value=0)
        years = st.slider("Loan term (years)", 1, 30, 5)

        df = get_data("sa/rates")
        if df is not None and not df.empty:
            rate = df["Value"].iloc[-1] / 100
            monthly_rate = rate / 12

            months = years * 12
            if monthly_rate > 0:
                payment = loan * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
            else:
                payment = loan / months

            st.write(f"estimated monthly payment: **R {payment:,.2f}**")
        else:
            st.warning("Interest-rate data unavailable.")

# ==========================================
#               FORECASTS SECTION
# ==========================================

if menu == "Forecasts":
    st.header("📈 Inflation Forecasts (SA & US)")

    col1, col2 = st.columns(2)

    # ---------------------------------------------
    # Helper to fetch forecast & build DataFrame
    # ---------------------------------------------

    def get_forecast_df(endpoint):
        try:
            r = requests.get(f"{API_BASE}/endpoint", timeout=10)
            if r.status_code != 200:
                return None
            
            data = r.json()
            fc = data["forecast"]
            lower = data["confidence_intervals"]["lower"]
            upper = data["confidence_intervals"]["upper"]

            df = pd.DataFrame({
                "Date": list(fc.keys()),
                "Forecast": list(fc.values()),
                "Lower": list(lower.values()),
                "Upper": list(upper.values())
            })
            return df
        except Exception as e:
            st.error(f"Forecast error: {e}")
            return None
        

