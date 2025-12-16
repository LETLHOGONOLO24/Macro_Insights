import numpy as np
import pandas as pd
from pmdarima import auto_arima

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing
from typing import Optional, Tuple

# --------------------------
# Helper utilities
# --------------------------

def series_from_df(df, value_col="Value", date_col="Date"):
    """
    Convert API DataFrame to clean time series for forecasting.
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty")

    s = df.copy()

    # Ensure datetime
    s[date_col] = pd.to_datetime(s[date_col])

    # Sort
    s = s.sort_values(date_col)

    # Set index
    s = s.set_index(date_col)

    # Select numeric series
    series = pd.Series(
        s[value_col].astype(float).values,
        index=pd.PeriodIndex(s.index, freq="Y"),
        name=value_col
    )

    # Drop missing values
    series = series.dropna()

    if len(series) < 10:
        raise ValueError("Not enough data points for ARIMA")

    return series


# --------------------------
# ARIMA Forecaster (annual)
# --------------------------

class AutoARIMAForecaster:
    def __init__(self):
        self.model = None
        self.fitted = None

    def fit(self, series):
        if series is None or len(series) < 10:
            raise ValueError("Series too short for ARIMA")

        self.model = pm.auto_arima(
            series,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore"
        )

        self.fitted = self.model

    def forecast(self, steps=5):
        if self.fitted is None:
            raise RuntimeError("Model not fitted")

        fc, ci = self.fitted.predict(
            n_periods=steps,
            return_conf_int=True
        )

        index = pd.period_range(
            start=self.fitted.arima_res_.data.endog.index[-1] + 1,
            periods=steps,
            freq="Y"
        )

        fc_series = pd.Series(fc, index=index, name="forecast")

        ci_df = pd.DataFrame(
            ci,
            index=index,
            columns=["lower", "upper"]
        )

        return fc_series, ci_df

    
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

