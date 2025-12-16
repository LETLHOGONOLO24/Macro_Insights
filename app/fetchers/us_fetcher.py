import requests
import pandas as pd

class USFetcher:
    def __init__(self):
        self.base = "https://api.worldbank.org/v2/country/USA/indicator"

    def _fetch(self, indicator):
        url = f"{self.base}/{indicator}?format=json&per_page=2000"

        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()

            # World Bank error response
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

    def fetch_gdp_growth(self):
        return self._fetch("NY.GDP.MKTP.KD.ZG")

    def fetch_real_interest_rate(self):
        return self._fetch("FR.INR.RINR")

