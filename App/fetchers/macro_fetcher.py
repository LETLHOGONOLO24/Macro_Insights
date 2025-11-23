from fetchers.south_africa import SouthAfricaFetcher
from fetchers.us_fetcher import USFetcher

class MacroFetcher:
    def __init__(self, country):
        self.country = country.lower()

    if self.country == "south africa" or self.country == "za" or self.country == "zaf":
        self.fetcher = SouthAfricaFetcher()

    elif self.country == "united states" or self.country == "us" or self.country == "usa":
        self.fetcher = USFetcher()

    else:
        raise ValueError(f"Country '{country}' is not supported yet.")
    
# ------------------------------
# Unified Fetch Function
# ------------------------------

def inflation(self):
    return self.fetcher.fetch_inflation()

def lending_rate(self):
    return self.fetcher.fetch_lending_rate()

def interest_rate(self):
    """For US -> real interest rate, For SA -> repo rate (or lending)."""

    if isinstance(self.fetcher, SouthAfricaFetcher()):
        return self.fetcher.fetch_lending_rate()
    else:
        return self.fetcher.fetch_real_interest_rate()
    
def gdp_growth(self):
    return self.fetcher.fetch_gdp_growth()