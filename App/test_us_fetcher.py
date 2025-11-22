from fetchers.us_fetcher import USFetcher

us = USFetcher()

print("\n📌 US Inflation:")
print(us.fetch_inflation().tail())

print("\n📌 US Lending Rate:")
print(us.fetch_lending_rate().tail())

print("\n📌 US Real Interest Rate:")
print(us.fetch_real_interest_rate().tail())

print("\n📌 US GDP Growth:")
print(us.fetch_gdp_growth().tail())