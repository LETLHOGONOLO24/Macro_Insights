from fetchers.macro_fetcher import MacroFetcher
import pandas as pd

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def main():
    print_header("🌍 Macro Insights - Unified Macro Fetcher")

    # User chooses country
    country = input("Enter a country (South Africa / USA): ").strip()

    try:
        fetcher = MacroFetcher(country)
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # ---------------------------------------------------------
    # FETCH BASE DATA
    # ---------------------------------------------------------

    print_header(f"📌 Fetching inflation data for {country}")
    inflation_df = fetcher.inflation()
    print(inflation_df.tail())

    print_header(f"📌 Fetching lending/interest rate data for {country}")
    rate_df = fetcher.lending_rate()
    print(rate_df.tail())

    print_header(f"📌 Fetching GDP growth data for {country}")
    gdp_df = fetcher.gdp_growth()
    print(gdp_df.tail())

    # --------------------------------------------------------
    # PLACEHOLDER FOR FORECASTING ENGINE
    # (I will build this next)
    # --------------------------------------------------------

    print_header("🤖 Forecasting module is coming next...")

if __name__ == "__main__":
    main()