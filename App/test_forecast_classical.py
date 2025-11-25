# app/test_forecast_classical.py
from fetchers.macro_fetcher import MacroFetcher
from Forecasting.classical import (
    series_from_df,
    ARIMAForecaster,
    HoltWintersForecaster,
    quick_compare,
    AutoARIMAForecaster
)

# Choose country
mf = MacroFetcher("south africa")   # or "usa"

# Fetch inflation series (World Bank annual)
infl_df = mf.inflation()
print("Inflation fetched:")
print(infl_df)

# Convert to pandas Period series (annual)
infl_series = series_from_df(infl_df)

print("Series preview:")
print(infl_series.tail())

# ARIMA forecasting
arima = ARIMAForecaster(p=1, d=1, q=0)
fitted_tail, arima_fc = quick_compare(infl_series, arima, steps=3)
print("\nARIMA - last fitted values:")
print(fitted_tail)
print("\nARIMA - forecasts:")
print(arima_fc)

# Holt-Winters forecasting
hw = HoltWintersForecaster(trend="add")
fitted_tail_hw, hw_fc = quick_compare(infl_series, hw, steps=3)
print("\nHolt-Winters - forecasts:")
print(hw_fc)

print("\nAuto-ARIMA Forecast:")
auto_arima_model = AutoARIMAForecaster()
auto_arima_model.fit(infl_series)
auto_fc = auto_arima_model.forecast(3)
print(auto_fc)
