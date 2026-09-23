"""!
@file test_data_loader.py
@author Siddhanth
@date 2026-04-27
@brief Unit tests for the data loader module.

This module contains pytest unit tests to ensure that the Destatis CPI dataset 
is loaded correctly, datatypes are enforced, and the Time Series index is 
strictly set to a monthly frequency.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import load_cpi_data

def test_load_cpi_data_success():
    """Test if the dataset loads correctly and maintains proper formatting."""
    # Note: Assumes running from project root where data/61111-0002_en.csv exists
    # For testing, we mock a filepath or ensure the real one works.
    
    # We will test against the real dataset since it's a fixed CSV in the repo.
    df = load_cpi_data(filepath="data/61111-0002_en.csv")
    
    assert not df.empty, "Dataframe should not be empty."
    assert 'CPI' in df.columns, "Dataframe must contain 'CPI' column."
    
    # Verify index is DatetimeIndex
    assert isinstance(df.index, pd.DatetimeIndex), "Index must be a pandas DatetimeIndex."
    
    # Verify strict monthly frequency (MS = Month Start)
    assert df.index.freqstr == 'MS', "Frequency must be set to Month Start (MS)."

def test_load_cpi_data_missing_file():
    """Test that a proper FileNotFoundError is raised for invalid paths."""
    with pytest.raises(FileNotFoundError):
        load_cpi_data(filepath="data/nonexistent_file.csv")

def test_data_types_and_missing_values():
    """Verify that CPI values are floats and there are no NaN values after load."""
    df = load_cpi_data(filepath="data/61111-0002_en.csv")
    
    # Values should be numeric
    assert pd.api.types.is_numeric_dtype(df['CPI']), "CPI column must be numeric."
    
    # Should not have missing values within the trimmed timeframe
    assert not df['CPI'].isnull().any(), "There should be no missing values in the final CPI series."
