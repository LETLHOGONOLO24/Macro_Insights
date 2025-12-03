import requests
import pandas as pd

class USFetcher:
    def __init__(self):
        self.base = "https://api.worldbank.org/v2/country/USA/indicator"

    def _fetch(self, indicator):
        """Fetch and clean US data from World Bank API."""
        url = f"{self.base}/{indicator}?format=json&per_page=2000"

        try:
            response = requests.get(url)
            data = response.json()

            if len(data) < 2 or data[1] is None:
                print(f"⚠️ No data found for indicator {indicator}")
                return pd.DataFrame()

            raw = data[1]

            df = pd.DataFrame([
                {"Date": entry["date"], "Value": entry["value"]}
                for entry in raw
                if entry["value"] is not None and entry["date"] is not None
            ])

            if df.empty:
                return df

            # --- FIX: Convert Year String → Datetime ---
            df["Date"] = pd.to_datetime(df["Date"], format="%Y", errors="coerce")
            df = df.dropna(subset=["Date"])
            df = df.sort_values("Date")

            # Add Year column
            df["Year"] = df["Date"].dt.year.astype(int)

            return df

        except Exception as e:
            print(f"❌ World Bank fetch error for {indicator}: {e}")
            return pd.DataFrame()

    # ---------------------------
    # PUBLIC FETCH METHODS
    # ---------------------------

    def fetch_inflation(self):
        return self._fetch("FP.CPI.TOTL.ZG")

    def fetch_lending_rate(self):
        return self._fetch("FR.INR.LEND")

    def fetch_real_interest_rate(self):
        return self._fetch("FR.INR.RINR")

    def fetch_gdp_growth(self):
        return self._fetch("NY.GDP.MKTP.KD.ZG")
