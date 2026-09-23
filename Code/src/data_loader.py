"""!
@file data_loader.py
@author Siddhanth
@date 2026-04-27
@brief Data Loader Module for Destatis CPI Dataset.

This module provides the central standard interface for loading the raw 
Consumer Price Index data, cleaning it, and returning a strict Time Series 
object ready for modeling.
"""

import pandas as pd
import numpy as np
import os

def load_cpi_data(filepath="data/61111-0002_en.csv"):
    """!
    @brief Loads and preprocesses the Destatis CPI dataset (Table 61111-0002).
    
    This function reads the CSV, parses the textual months into numeric formats, 
    cleans missing or structural dots, and enforces a strict monthly DatetimeIndex 
    which is required by the statsmodels time series algorithms.

    @param filepath The relative or absolute path to the Destatis CSV file. Defaults to 'data/61111-0002_en.csv'.
    @return A pandas DataFrame containing a single 'CPI' column indexed by a strict monthly DatetimeIndex ('MS').
    @exception FileNotFoundError If the specified CSV file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at {filepath}")

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
        
    data_lines = []
    for line in lines[6:]: # Skip the first 6 lines (headers/metadata)
        if line.startswith('__________') or line.startswith('"') or line.startswith('©') or line.startswith('created:'):
            break # Stop reading when we hit the footer
            
        parts = line.strip().split(';')
        if len(parts) >= 3:
            data_lines.append(parts[:8]) # We only need up to index 7
        
    df = pd.DataFrame(data_lines)
    # Fill missing columns if some lines were short
    for i in range(df.shape[1], 8):
        df[i] = np.nan
        
    df.columns = ['Year', 'Month', 'CPI', 'Status_CPI', 'YoY', 'Status_YoY', 'MoM', 'Status_MoM']
    
    # Forward fill the Year (it's only populated on January rows)
    df['Year'] = df['Year'].replace('', np.nan)
    df['Year'] = df['Year'].ffill()
    
    # Map textual months to zero-padded numeric strings
    month_map = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }
    df['Month_Num'] = df['Month'].map(month_map)
    
    # Drop rows where the month wasn't recognized (e.g. empty rows or bad parse)
    df = df.dropna(subset=['Month_Num'])
    
    # Create the DatetimeIndex
    df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month_Num'])
    df.set_index('Date', inplace=True)
    
    # Clean the CPI column: replace '...' (future/missing) and '.' with NaN
    df['CPI'] = df['CPI'].replace('...', np.nan).replace('.', np.nan)
    # Convert to numeric
    df['CPI'] = pd.to_numeric(df['CPI'], errors='coerce')
    
    # Drop future months where CPI is missing
    df = df.dropna(subset=['CPI'])
    
    # Sort index just in case
    df = df.sort_index()
    
    # Set strict monthly start frequency
    df = df.asfreq('MS')
    
    # Return only the clean CPI time series
    return df[['CPI']]

if __name__ == "__main__":
    df = load_cpi_data()
    print(f"Data Loaded Successfully!")
    print(f"Total observations: {len(df)}")
    print(f"Date Range: {df.index.min().date()} to {df.index.max().date()}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())
