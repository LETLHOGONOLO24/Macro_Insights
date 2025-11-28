from fetchers.south_africa import SouthAfricaFetcher

fetcher = SouthAfricaFetcher()

print("\nInflation:")
print(fetcher.fetch_lending_rate().tail())

print("\nLending Rate:")
print(fetcher.fetch_inflation().tail())

print("\nGDP Growth:")
print(fetcher.fetch_gdp_growth().tail())