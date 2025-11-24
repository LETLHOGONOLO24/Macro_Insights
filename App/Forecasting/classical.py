import numpy as np
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing
from typing import Optional, Tuple

# --------------------------
# Helper utilities
# --------------------------

def series_from_df(df: pd.DataFrame, date_col: str = "Date", value_col: str = "Value") -> pd.Series:
    """
    Converts a DataFrame returned by the fetchers into a pandas.Series indexed by Period (year).
    Assumes df has a 'Date' column of datetime-like (or integer year) and a 'Value' column.
    Returns a Series with dtype float and annaul PeriodIndex
    """

    if df is None or df.empty:
        return pd.Series(dtype=float)
    
    # Normalize date to year if needed
    s = df.copy()
    # If Date is a datetime, convert to year int
    if pd.api.types.is_datetime64_any_dtype(s["Date"]):
        s["Year"] = s["Date"].dt.year
    else:
        s["Year"] = s["Date"].astype(int)

    s = s.dropna(subset=["Year", value_col])
    s = s.drop_duplicates(subset=["Year"])
    s = s.sort_values("Year")
    series = pd.Series(data=s[value_col].astype(float).values, index=pd.PeriodIndex(s["Year"].astype(int), freq='A'), name=value_col)
    return series

# --------------------------
# ARIMA Forecaster (annual)
# --------------------------

class ARIMAForecaster:
    """
    Simple ARIMA forecaster for annual data.
    We can provide p, d, q orders or let it default to (1,1,0) which is robust for many annual series.
    """

    def __init__(self, p: int = 1, d: int = 1, q: int = 0):
        self.order = (p, d, q)
        self.model = None
        self.fitted = None
        self.training_series: Optional[pd.Series] = None

    def fit(self, series: pd.Series):
        """
        Fit ARIMA to an annual pandas Series (PEriodIndex).
        """
        if series is None or series.empty:
            raise ValueError("Empty series provided to ARIMAForecaster.fit")
        
        # Convert PeriodIndex to DatetimeIndex by taking period start to satisfy statsmodels

        ts = series.copy().to_timestamp()
        self.training_series = ts
        self.model = ARIMA(ts, order=self.order)
        self.fitted = self.model.fit()
        return self.fitted
    
    def forecast(self, steps: int = 1) -> pd.Series:
        """
        Forecast the next `steps` years. Returns a pandas Series indexed by Period with freq 'A'.
        """
        if self.fitted is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        pred = self.fitted.get_forecast(steps=steps)
        fc_index = pd.period_range(start=self.training_series.index[-1].to_period('A') + 1, periods=steps, freq='A')
        values = pred.predicted_mean.values
        return pd.Series(data=values, index=fc_index, name="ARIMA_forecast")
    
# ---------------------------
# Holt-Winters / Exponential Smoothing Forecaster (annual)
# ---------------------------

class HoltWintersForecaster:
    """
    For annual data where seasonality is not meaningful, we use:
      - Exponential Smoothing (non-seasonal) for longer series
      - SimpleExpSmoothing for short series.
    Expects a pandas Series with PeriodIndex (annual).
    """

    def __init__(self, trend="add"):
        self.trend = trend
        self.fitted = None
        self.training_series = None

    def fit(self, series: pd.Series):
        if series is None or series.empty:
            raise ValueError("Empty series provided to HoltWintersForecaster.fit")
        
        ts = series.copy().to_timestamp()
        self.training_series = ts

        # Very short series -> SimpleExpSmoothing
        if len(ts) < 5:
            model = SimpleExpSmoothing(ts)
            self.fitted = model.fit() # <- MUST HAVE PARENTHESES
        else:
            model = ExponentialSmoothing(ts, trend=self.trend, seasonal=None)
            self.fitted = model.fit() # <- MUST HAVE PARENTHESES
        return self.fitted
    
    def forecast(self, steps: int = 1) -> pd.Series:
        if self.fitted is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        pred = self.fitted.forecast(steps)
        fc_index = pd.period_range(
            start=self.training_series.index[-1].to_period('Y') + 1,
            periods=steps,
            freq='Y'
        )

        return pd.Series(pred.values, index=fc_index, name="HoltWinters_forecast")
    

# ---------------------------
# Utility: quick_compare
# ---------------------------

def quick_compare(series: pd.Series, forecaster, steps: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    Fit forecaster on series and return (fitted_values_last, forecast_values)
    fitted_values_last: last few fitted points (for diagnostics)
    forecast_values: next 'steps' forecasted values
    forecaster: an instance of ARIMAForecaster or HoltWintersForecaster
    """
    forecaster.fit(series)
    forecast = forecaster.forecast(steps=steps)
    fitted_tail = forecaster.training_series.tail(5)
    return fitted_tail, forecast

