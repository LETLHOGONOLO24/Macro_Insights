import numpy as np
import pandas as pd
from pmdarima import auto_arima

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

class AutoARIMAForecaster:
    """
    Automatic ARIMA forecaster using AIC model selection.
    Automatically chooses p, d, q based on:
      - stationarity tests
      - differencing tests
      - AIC, AICc, BIC
    Very useful for macroeconomic annual data.
    """

    def __init__(self,
                 seasonal=False,
                 m=1,
                 max_p=5,
                 max_d=2,
                 max_q=5,
                 information_criterion='aic'):

        self.seasonal = seasonal
        self.m = m
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q
        self.information_criterion = information_criterion

        self.model = None
        self.fitted = None
        self.training_series = None

    def fit(self, series: pd.Series):
        """
        Fit Auto-ARIMA on annual data (PeriodIndex -> DatetimeIndex).
        """
        if series is None or series.empty:
            raise ValueError("Empty series provided to AutoARIMAForecaster.fit")
        
        ts = series.copy().to_timestamp(freq='Y')
        self.training_series = ts

        self.model = auto_arima(
            ts,
            seasonal=self.seasonal,
            m=self.m,
            max_p=self.max_p,
            max_d=self.max_d,
            max_q=self.max_q,
            information_criterion=self.information_criterion,
            trace=False,
            suppress_warnings=True
        )

        self.fitted = self.model
        return self.fitted
    
    def forecast(self, steps: int = 1, alpha: float = 0.05):
        """
        Forecast future values with confidence intervals.

        Parameters:
            steps (int): Number of periods to forecast.
            alpha (float): Significance level (0.05 = 95% confidence interval).

        Returns:
            forecast (pd.Series)
            conf_int (pd.DataFrame) with columns ["lower", "upper"]
        """
        if self.fitted is None:
            raise RuntimeError("Auto-ARIMA model not fitted. Call fit() first.")
        
        # Auto-ARIMA returns both forecasts and confidence intervals
        pred, conf_int = self.fitted.predict(
            n_periods=steps,
            return_conf_int=True,
            alpha=alpha
        )

        forecast = pd.Series(pred.values, index=pred.index, name="AutoARIMA_forecast")

        # Build CI DataFrame
        conf_df = pd.DataFrame({
            "lower": conf_int[:, 0],
            "upper": conf_int[:, 1]
        }, index=forecast.index)

        return forecast, conf_df

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

