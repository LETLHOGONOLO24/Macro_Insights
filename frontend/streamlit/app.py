import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================
# Configuration
# ============================

API_BASE = os.getenv("API_BASE", "http://macro_api:5000/api")

st.set_page_config(
    page_title="Macro Insights Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Macro Insights – Economic Dashboard")

# ============================
# API Helpers
# ============================

def get_data(endpoint):
    """Fetch standard time-series data"""
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        if r.status_code == 200:
            df = pd.DataFrame(r.json())
            return df if not df.empty else None
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def get_forecast(endpoint):
    """Fetch forecast JSON (NOT a DataFrame)"""
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        st.error(f"Forecast API error: {e}")
        return None


def forecast_json_to_df(fc_json):
    """Convert forecast JSON to DataFrame"""
    return pd.DataFrame({
        "Forecast": fc_json["forecast"],
        "Lower": fc_json["confidence_intervals"]["lower"],
        "Upper": fc_json["confidence_intervals"]["upper"]
    })


# ============================
# Sidebar Navigation
# ============================

menu = st.sidebar.radio(
    "Navigation",
    ["South Africa", "United States", "Forecasts", "Tools"]
)

# ==================================
# SOUTH AFRICA
# ==================================

if menu == "South Africa":
    st.header("🇿🇦 South Africa – Economic Indicators")

    tab1, tab2, tab3 = st.tabs(["Inflation", "GDP Growth", "Interest Rates"])

    # Inflation
    with tab1:
        df = get_data("sa/inflation")
        if df is not None:
            st.subheader("Inflation (%)")
            st.line_chart(df.set_index("Date")["Value"])

            if st.button("📈 View Inflation Forecast (SA)"):
                fc = get_forecast("sa/inflation/forecast")

                if fc and "forecast" in fc:
                    fc_df = forecast_json_to_df(fc)
                    st.subheader("Inflation Forecast (ARIMA)")
                    st.line_chart(fc_df)
                else:
                    st.warning("No forecast available")
        else:
            st.warning("No inflation data available.")

    # GDP
    with tab2:
        df = get_data("sa/gdp")
        if df is not None:
            st.subheader("GDP Growth (%)")
            st.line_chart(df.set_index("Date")["Value"])
        else:
            st.warning("No GDP data available.")

    # Rates
    with tab3:
        df = get_data("sa/rates")
        if df is not None:
            st.subheader("Repo / Lending Rate (%)")
            st.line_chart(df.set_index("Date")["Value"])
        else:
            st.warning("No interest-rate data available.")

# ==================================
# UNITED STATES
# ==================================

if menu == "United States":
    st.header("🇺🇸 United States – Economic Indicators")

    tab1, tab2, tab3 = st.tabs(["Inflation", "GDP Growth", "Interest Rates"])

    # Inflation
    with tab1:
        df = get_data("us/inflation")
        if df is not None:
            st.subheader("Inflation (%)")
            st.line_chart(df.set_index("Date")["Value"])

            if st.button("📈 View Inflation Forecast (US)"):
                fc = get_forecast("us/inflation/forecast")

                if fc and "forecast" in fc:
                    fc_df = forecast_json_to_df(fc)
                    st.subheader("Inflation Forecast (ARIMA)")
                    st.line_chart(fc_df)
                else:
                    st.warning("No forecast available")
        else:
            st.warning("No inflation data available.")

    # GDP
    with tab2:
        df = get_data("us/gdp")
        if df is not None:
            st.subheader("GDP Growth (%)")
            st.line_chart(df.set_index("Date")["Value"])
        else:
            st.warning("No GDP data available.")

    # Rates
    with tab3:
        df = get_data("us/real_rates")
        if df is not None:
            st.subheader("Interest Rates (%)")
            st.line_chart(df.set_index("Date")["Value"])
        else:
            st.warning("No interest-rate data available.")

# ==================================
# FORECASTS PAGE (Dedicated)
# ==================================

if menu == "Forecasts":
    st.header("📈 Inflation Forecasts (ARIMA)")

    col1, col2 = st.columns(2)

    # SA Forecast
    with col1:
        st.subheader("🇿🇦 South Africa")

        fc = get_forecast("sa/inflation/forecast")

        if fc and "forecast" in fc:
            df = forecast_json_to_df(fc)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(df.index, df["Forecast"], label="Forecast")
            ax.fill_between(df.index, df["Lower"], df["Upper"], alpha=0.3, label="95% CI")
            ax.set_title("SA Inflation Forecast")
            ax.legend()

            st.pyplot(fig)
            st.dataframe(df)
        else:
            st.warning("No forecast available")

    # US Forecast
    with col2:
        st.subheader("🇺🇸 United States")

        fc = get_forecast("us/inflation/forecast")

        if fc and "forecast" in fc:
            df = forecast_json_to_df(fc)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(df.index, df["Forecast"], label="Forecast")
            ax.fill_between(df.index, df["Lower"], df["Upper"], alpha=0.3, label="95% CI")
            ax.set_title("US Inflation Forecast")
            ax.legend()

            st.pyplot(fig)
            st.dataframe(df)
        else:
            st.warning("No forecast available")

# ==================================
# TOOLS
# ==================================

if menu == "Tools":
    st.header("🛠️ Tools & Calculators")

    tool = st.selectbox(
        "Choose a tool:",
        ["🏪 Grocery Inflation", "🏦 Loan Calculator"]
    )

    # Grocery Inflation
    if tool == "🏪 Grocery Inflation":
        st.subheader("Grocery Inflation Estimator")

        amount = st.number_input("Monthly grocery spend (R)", min_value=0.0)

        df = get_data("sa/inflation")
        if df is not None:
            latest = df["Value"].iloc[-1] / 100
            adjusted = amount * (1 + latest)
            st.write(f"Inflation-adjusted cost: **R {adjusted:,.2f}**")
        else:
            st.warning("Inflation data unavailable")

    # Loan Calculator
    if tool == "🏦 Loan Calculator":
        st.subheader("Loan Payment Calculator")

        loan = st.number_input("Loan amount (R)", min_value=0.0)
        years = st.slider("Loan term (years)", 1, 30, 5)

        df = get_data("sa/rates")
        if df is not None:
            rate = df["Value"].iloc[-1] / 100 / 12
            months = years * 12

            payment = (
                loan * rate * (1 + rate) ** months /
                ((1 + rate) ** months - 1)
            ) if rate > 0 else loan / months

            st.write(f"Estimated monthly payment: **R {payment:,.2f}**")
        else:
            st.warning("Interest-rate data unavailable")
