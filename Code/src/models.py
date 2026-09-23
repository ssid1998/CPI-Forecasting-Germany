"""!
@file models.py
@author Siddhanth
@date 2026-04-27
@brief Time Series Modeling Interface Module.

This module provides a unified API for interacting with `statsmodels` 
implementations of ARIMA, ETS, and SARIMA models. It ensures standardized 
`.fit()` and `.predict()` methods across models to support automated testing,
evaluation pipelines, and user-facing dashboards.
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.statespace.sarimax import SARIMAX

class TimeSeriesModelInterface:
    """!
    @brief Abstract Base Class for all forecasting models used in the system.
    
    Ensures that any model added to the workflow adheres to a consistent
    interface, reducing code duplication in automated evaluation scripts.
    """
    def __init__(self, **kwargs):
        """!
        @brief Initializes the model with specific hyperparameters.
        @param kwargs Key-value pairs of hyperparameters.
        """
        self.params = kwargs
        self.model_fit = None

    def fit(self, train_series: pd.Series):
        """!
        @brief Fits the underlying statistical model to a historical training series.
        @param train_series The endogenous variable (target).
        @exception NotImplementedError If the child class does not implement this.
        """
        raise NotImplementedError("Must implement fit method")

    def predict(self, steps: int) -> pd.Series:
        """!
        @brief Forecasts future values.
        @param steps The number of future periods to predict.
        @return A pandas Series of point forecasts.
        @exception NotImplementedError If the child class does not implement this.
        """
        raise NotImplementedError("Must implement predict method")
        
    def get_confidence_intervals(self, steps: int, alpha: float = 0.05) -> pd.DataFrame:
        """!
        @brief Generates lower and upper bounds of a prediction interval.
        @param steps The number of periods to forecast into the future.
        @param alpha Significance level (0.05 = 95% interval, 0.20 = 80%).
        @return A pandas DataFrame with two columns ('lower CPI', 'upper CPI').
        @exception NotImplementedError If the model cannot provide intervals.
        """
        raise NotImplementedError("Must implement confidence intervals if supported")


class ARIMAModel(TimeSeriesModelInterface):
    """!
    @brief Auto-Regressive Integrated Moving Average (ARIMA) Model Wrapper.
    """
    def fit(self, train_series: pd.Series):
        """!
        @brief Fits statsmodels.tsa.arima.model.ARIMA using provided orders.
        @param train_series The endogenous variable.
        """
        order = self.params.get('order', (1, 1, 1))
        model = ARIMA(train_series, order=order)
        self.model_fit = model.fit()

    def predict(self, steps: int) -> pd.Series:
        """!
        @brief Generates ARIMA point forecasts.
        @param steps Number of steps to forecast.
        @return Forecast series.
        """
        return self.model_fit.forecast(steps=steps)
        
    def get_confidence_intervals(self, steps: int, alpha: float = 0.05) -> pd.DataFrame:
        """!
        @brief Generates ARIMA prediction intervals.
        @param steps Steps to forecast.
        @param alpha Significance level.
        @return DataFrame with confidence bounds.
        """
        forecast = self.model_fit.get_forecast(steps=steps)
        return forecast.conf_int(alpha=alpha)


class ETSModelWrapper(TimeSeriesModelInterface):
    """!
    @brief Error, Trend, Seasonal (ETS) Exponential Smoothing Wrapper.
    """
    def fit(self, train_series: pd.Series):
        """!
        @brief Fits statsmodels ETS model with trend and seasonality parameters.
        @param train_series The endogenous variable.
        """
        trend = self.params.get('trend', 'add')
        seasonal = self.params.get('seasonal', 'add')
        seasonal_periods = self.params.get('seasonal_periods', 12)
        model = ETSModel(train_series, error='add', trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
        self.model_fit = model.fit(disp=False)

    def predict(self, steps: int) -> pd.Series:
        """!
        @brief Generates ETS point forecasts.
        @param steps Number of steps to forecast.
        @return Forecast series.
        """
        return self.model_fit.forecast(steps=steps)
        
    def get_confidence_intervals(self, steps: int, alpha: float = 0.05) -> pd.DataFrame:
        """!
        @brief Generates exact ETS state-space prediction intervals.
        @param steps Steps to forecast.
        @param alpha Significance level.
        @return DataFrame with confidence bounds.
        """
        start_idx = len(self.model_fit.data.endog)
        end_idx = start_idx + steps - 1
        
        pred_res = self.model_fit.get_prediction(start=start_idx, end=end_idx)
        ci = pred_res.pred_int(alpha=alpha)
        
        # Ensure column names are standard so app.py finds them
        ci.columns = ['lower CPI', 'upper CPI']
        return ci


class SARIMAModel(TimeSeriesModelInterface):
    def fit(self, train_series: pd.Series):
        order = self.params.get('order', (1, 1, 1))
        seasonal_order = self.params.get('seasonal_order', (1, 1, 1, 12))
        model = SARIMAX(train_series, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
        self.model_fit = model.fit(disp=False)

    def predict(self, steps: int) -> pd.Series:
        return self.model_fit.forecast(steps=steps)
        
    def get_confidence_intervals(self, steps: int, alpha: float = 0.05) -> pd.DataFrame:
        forecast = self.model_fit.get_forecast(steps=steps)
        return forecast.conf_int(alpha=alpha)
