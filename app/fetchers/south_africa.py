import pandas as pd
import requests

class SouthAfricaFetcher:
    def __init__(self):
        self.base = "https://api.worldbank.org/v2/country/ZAF/indicator"

    def _fetch(self, indicator):
        """Fetch and clean data from World Bank API (safe for Docker + K8s)."""
        url = f"{self.base}/{indicator}?format=json&per_page=2000"

        try:
            response = requests.get(url)
            data = response.json()

            # World Bank always returns: [metadata, data]
            if len(data) < 2 or data[1] is None:
                print(f"⚠️ No data found for indicator {indicator}")
                return pd.DataFrame()

            raw = data[1]

            # Build DataFrame safely
            df = pd.DataFrame([
                {
                    "Date": entry["date"],
                    "Value": entry["value"]
                }
                for entry in raw
                if entry["value"] is not None and entry["date"] is not None
            ])

            if df.empty:
                return df

            # --- FIX: Convert Date properly ---
            df["Date"] = pd.to_datetime(df["Date"], format="%Y", errors="coerce")
            df = df.dropna(subset=["Date"])

            # Sort by time
            df = df.sort_values("Date")

            # Add Year column for forecasting
            df["Year"] = df["Date"].dt.year.astype(int)

            return df

        except Exception as e:
            print(f"❌ World Bank fetch error for {indicator}: {e}")
            return pd.DataFrame()

    # ------------------------------
    # PUBLIC FETCH METHODS
    # ------------------------------

    def fetch_inflation(self):
        return self._fetch("FP.CPI.TOTL.ZG")

    def fetch_lending_rate(self):
        return self._fetch("FR.INR.LEND")

    def fetch_gdp_growth(self):
        return self._fetch("NY.GDP.MKTP.KD.ZG")

