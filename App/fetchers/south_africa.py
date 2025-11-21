import pandas as pd
import requests

class SouthAfricaFetcher:
    def __init__(self):

        # TradingEconomics free access
        self.api_base = "https://api.tradingeconomics.com"
        self.api_key = "guest:guest"

    def _fetch(self, endpoint):
        """ Internal method to fetch data and return cleaned DataFrame """

        url = f"{self.api_base}{endpoint}?c={self.api_key}"

        try:
            df = pd.read_json(url)
            if df.empty:
                print("⚠️ No data returned from TradingEconomics.")
                return df
            
            # Basic cleaning: sort by date
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            return df
        
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return pd.Dataframe()
        
    # -----------------------------
    # 📌 Public Fetcher Methods
    # -----------------------------

    def fetch_repo_rate(self):
        """Fetch SA repo / interest rate history."""

        endpoint = "/historical/country/south africa/indicator/interest rate"
        return self._fetch(endpoint)
    
    def fetch_inflation(self):
        """Fetch SA inflation rate YoY."""
        endpoint = "/historical/country/south africa/indicator/inflation rate"
        return self._fetch(endpoint)
    
    def fetch_prime_rate(self):
        """Fetch SA prime lending rate."""
        endpoint = "/historical/country/south africa/indicator/prime lending rate"
        return self._fetch(endpoint)