import pandas as pd
import requests
import urllib.parse

import requests
import pandas as pd

class SouthAfricaFetcher:
    def __init__(self):
        self.base = "https://api.worldbank.org/v2/country/ZAF/indicator"

    def _fetch(self, indicator):
        """Fetch and clean data from World Bank API."""
        url = f"{self.base}/{indicator}?format=json&per_page=2000"

        try:
            response = requests.get(url)
            data = response.json()

            # Data is returned as [metadata, actual_data]
            raw = data[1]

            df = pd.DataFrame([{
                "Date": int(entry["date"]),
                "Value": entry["value"]
            } for entry in raw])

            # Clean
            df = df.dropna()
            df["Date"] = pd.to_datetime(df["Date"], format="%Y")
            df = df.sort_values("Date")

            return df

        except Exception as e:
            print(f"❌ World Bank fetch error for {indicator}: {e}")
            return pd.DataFrame()

    # ------------------------------
    # PUBLIC FETCH METHODS
    # ------------------------------

    def fetch_inflation(self):
        """South Africa Inflation (annual %)."""
        return self._fetch("FP.CPI.TOTL.ZG")

    def fetch_lending_rate(self):
        """Lending interest rate (%). Closest match to SA bank rate."""
        return self._fetch("FR.INR.LEND")

    def fetch_gdp_growth(self):
        """GDP growth annual %."""
        return self._fetch("NY.GDP.MKTP.KD.ZG")
