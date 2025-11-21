import pandas as pd
import requests
import urllib.parse

class SouthAfricaFetcher:
    def __init__(self):
        self.base = "https://api.resbank.co.za/series"

    def _fetch_csv(self, series_code):
        """Fetch CSV data from SARB API, return cleaned DataFrame."""
        url = f"{self.base}/{series_code}/data?format=csv"

        try:
            df = pd.read_csv(url)
            # Clean date column
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            df = df.dropna()
            return df

        except Exception as e:
            print(f"❌ SARB error fetching {series_code}: {e}")
            return pd.DataFrame()

    # -----------------------------------
    # Public Fetch Methods
    # -----------------------------------

    def fetch_repo_rate(self):
        """South Africa Repo Rate (SARB series BIR/001)."""
        return self._fetch_csv("BIR/001")

    def fetch_prime_rate(self):
        """South Africa Prime Rate (SARB series BIR/002)."""
        return self._fetch_csv("BIR/002")

    def fetch_inflation(self):
        """South Africa CPI Headline Inflation YoY (KBP/6006)."""
        return self._fetch_csv("KBP/6006")