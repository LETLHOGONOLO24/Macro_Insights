import pandas as pd
import requests

class SouthAfricaFetcher:
    def __init__(self):
        # stable endpoint that avoids Azure API gateway redirects
        self.base = "https://api.worldbank.org/v2/country/ZAF/indicator"

        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

    def _fetch(self, indicator):
        url = f"{self.base}/{indicator}?format=json&per_page=2000"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            data = response.json()

            # Check if World Bank returns an error structure
            if not isinstance(data, list) or len(data) < 2:
                print("❌ Unexpected response:", data)
                return pd.DataFrame()

            raw = data[1]
            if raw is None:
                print("❌ Empty dataset:", data)
                return pd.DataFrame()

            df = pd.DataFrame([
                {
                    "Date": int(entry["date"]),
                    "Value": entry["value"]
                }
                for entry in raw
                if entry["value"] is not None
            ])

            df["Date"] = pd.to_datetime(df["Date"], format="%Y")
            df = df.sort_values("Date")

            return df

        except Exception as e:
            print("❌ World Bank fetch error:", e)
            return pd.DataFrame()

    def fetch_inflation(self):
        return self._fetch("FP.CPI.TOTL.ZG")

    def fetch_lending_rate(self):
        return self._fetch("FR.INR.RINR")
    
    def fetch_repo_rate(self):
        return self._fetch("FR.INR.RPOL")

    def fetch_gdp_growth(self):
        return self._fetch("NY.GDP.MKTP.KD.ZG")



