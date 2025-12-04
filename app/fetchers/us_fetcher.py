import requests
import pandas as pd

class USFetcher:
    def __init__(self):
        self.base = "https://api.worldbank.org/v2/country/USA/indicator"

    def _fetch(self, indicator):
        url = f"{self.base}/{indicator}?format=json&per_page=2000"
        try:
            response = requests.get(url)
            data = response.json()

            # Validate structure
            if not isinstance(data, list) or len(data) < 2 or data[1] is None:
                return pd.DataFrame()

            raw = data[1]

            rows = []
            for entry in raw:
                if entry["value"] is None:
                    continue

                # MAKE SURE DATE IS INT
                try:
                    year = int(entry["date"])
                except:
                    continue

                rows.append({
                    "Date": year,
                    "Value": entry["value"]
                })

            df = pd.DataFrame(rows)
            if df.empty:
                return df

            df["Date"] = pd.to_datetime(df["Date"], format="%Y")
            df = df.sort_values("Date")

            return df

        except Exception as e:
            print(f"❌ US fetch error for {indicator}: {e}")
            return pd.DataFrame()

    def fetch_inflation(self):
        return self._fetch("FP.CPI.TOTL.ZG")

    def fetch_gdp_growth(self):
        return self._fetch("NY.GDP.MKTP.KD.ZG")

    def fetch_real_interest_rate(self):
        return self._fetch("FR.INR.RINR")

