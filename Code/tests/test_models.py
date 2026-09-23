"""!
@file test_models.py
@author Siddhanth
@date 2026-04-27
@brief Unit tests for the time series models.

This module contains pytest unit tests to ensure that all implemented
time series models (ARIMA, ETS, SARIMA) conform to the TimeSeriesModelInterface
and correctly fit, predict, and generate confidence intervals without throwing errors.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import TimeSeriesModelInterface, ARIMAModel, ETSModelWrapper, SARIMAModel

@pytest.fixture
def mock_ts_data():
    """Generates a simple synthetic time series dataset for testing."""
    dates = pd.date_range(start='2020-01-01', periods=24, freq='MS')
    # Linear trend with small noise
    values = np.linspace(100, 120, 24) + np.random.normal(0, 1, 24)
    return pd.Series(values, index=dates, name='CPI')

def test_interface_not_implemented():
    """Test that the base interface properly raises NotImplementedError."""
    model = TimeSeriesModelInterface()
    with pytest.raises(NotImplementedError):
        model.fit(pd.Series([1, 2, 3]))
    with pytest.raises(NotImplementedError):
        model.predict(5)
    with pytest.raises(NotImplementedError):
        model.get_confidence_intervals(5)

def test_arima_model(mock_ts_data):
    """Test ARIMA model initialization, fitting, predicting, and CI generation."""
    model = ARIMAModel(order=(1, 1, 0))
    
    # Test Fitting
    model.fit(mock_ts_data)
    assert model.model_fit is not None, "Model fit object should be populated."
    
    # Test Prediction
    preds = model.predict(steps=5)
    assert len(preds) == 5, "Prediction should return exactly 5 steps."
    assert isinstance(preds, pd.Series), "Prediction should be a pandas Series."
    
    # Test CI
    ci = model.get_confidence_intervals(steps=5, alpha=0.05)
    assert len(ci) == 5, "Confidence intervals should have 5 rows."
    assert ci.shape[1] == 2, "Confidence intervals should have lower and upper bounds."

def test_ets_model(mock_ts_data):
    """Test ETS model behavior."""
    # Use additive trend, no seasonal to keep it simple for 24 periods
    model = ETSModelWrapper(trend='add', seasonal=None)
    
    model.fit(mock_ts_data)
    assert model.model_fit is not None, "ETS fit object should be populated."
    
    preds = model.predict(steps=3)
    assert len(preds) == 3, "Prediction should return exactly 3 steps."
    
    ci = model.get_confidence_intervals(steps=3, alpha=0.10)
    assert len(ci) == 3
    assert 'lower CPI' in ci.columns and 'upper CPI' in ci.columns

def test_sarima_model(mock_ts_data):
    """Test SARIMA model behavior."""
    # Simplified SARIMA
    model = SARIMAModel(order=(1, 0, 0), seasonal_order=(0, 0, 0, 12))
    
    model.fit(mock_ts_data)
    assert model.model_fit is not None
    
    preds = model.predict(steps=4)
    assert len(preds) == 4
    
    ci = model.get_confidence_intervals(steps=4, alpha=0.05)
    assert len(ci) == 4
    assert ci.shape[1] == 2
