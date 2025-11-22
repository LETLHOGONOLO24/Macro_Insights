import requests
import pandas as pd

class USFetcher:
    def __init__(self):
        # USA country code = USA
        self.base = "https://api.worldbank.ord/v2/country/USA/indicator"

    def _fetch(self, indicator):
        """Fetch and clean data from World Bank API."""
        url = f"{self.base}/{indicator}?format=json&per_page=2000"

        try:
            response = requests.get(url)
            data = response.json()

            raw = data[1]

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
            print(f"❌ World Bank fetch error for {indicator}: {e}")
            return pd.DataFrame()
        
    # ---------------------------
    # PUBLIC FETCH METHODS
    # ---------------------------

    def fetch_inflation(self):
        """US Inflation (annual %)."""
        return self._fetch("FP.CPI.TOTL.ZG")
    
    def fetch_lending_rate(self):
        """US Lending interest rate (%)."""
        return self._fetch("FR.INR.LEND")
    
    def fetch_real_interest_rate(self):
        """Real interest rate (inflation-adjusted)."""
        return self._fetch("FR.INR.RINR")
    
    def fetch_gdp_growth(self):
        """GDP Growth (annual %)."""
        return self._fetch("NY.GDP.MKTP.KD.ZG")