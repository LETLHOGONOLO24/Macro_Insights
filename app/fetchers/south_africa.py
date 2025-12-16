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
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()

            # Check if World Bank returns an error structure
            if not isinstance(data, list) or len(data) < 2:
                print("❌ World Bank returned invalid structure")
                return pd.DataFrame()

            rows = []
            for entry in data[1]:
                if entry["value"] is not None:
                    rows.append({
                        "Date": pd.to_datetime(entry["date"], format="%Y"),
                        "Value": float(entry["value"])
                    })

            df = pd.DataFrame(rows)

            if df.empty:
                print("⚠️ World Bank returned empty dataset")
                return df

            return df.sort_values("Date")

        except Exception as e:
            print(f"❌ Fetch error for {indicator}: {e}")
            return pd.DataFrame()

    def fetch_inflation(self):
        return self._fetch("FP.CPI.TOTL.ZG")

    def fetch_lending_rate(self):
        return self._fetch("FR.INR.RINR")
    
    def fetch_repo_rate(self):
        return self._fetch("FR.INR.RPOL")

    def fetch_gdp_growth(self):
        df = self._fetch("NY.GDP.MKTP.KD.ZG")
        return df.dropna()



