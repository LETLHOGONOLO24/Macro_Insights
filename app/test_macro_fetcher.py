from fetchers.macro_fetcher import MacroFetcher

print("\n🇿🇦 South Africa Inflation:")
sa = MacroFetcher("south africa")
print(sa.inflation().tail())

print("\n🇿🇦 South Africa Lending Rate:")
print(sa.lending_rate().tail())

print("\n🇺🇸 US Inflation:")
us = MacroFetcher("usa")
print(us.inflation().tail())

print("\n🇺🇸 US GDP Growth:")
print(us.gdp_growth().tail())