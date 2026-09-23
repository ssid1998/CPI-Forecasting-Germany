"""!
@file eda_pipeline.py
@author Siddhanth
@date 2026-04-27
@brief Exploratory Data Analysis Pipeline

This script performs EDA on the CPI dataset, generating visualizations
for time series progression, decomposition, and stationarity tests (ADF).
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from data_loader import load_cpi_data

def run_eda():
    # Ensure plots directory exists
    os.makedirs('plots', exist_ok=True)

    print("Loading data for EDA...")
    df = load_cpi_data()
    print(f"Data loaded successfully. Shape: {df.shape}, Range: {df.index.min().date()} to {df.index.max().date()}")

    # 1. EDA Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['CPI'], color='blue', label='Germany CPI (2020=100)')
    plt.title('Germany Consumer Price Index (1991-2026)')
    plt.xlabel('Date')
    plt.ylabel('CPI')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('plots/cpi_historical.png')
    plt.close()
    print("Saved historical CPI plot.")

    # 2. Stationarity Check (ADF Test)
    def print_adf(series, title):
        result = adfuller(series.dropna())
        print(f"\n--- ADF Test: {title} ---")
        print(f"ADF Statistic: {result[0]:.4f}")
        print(f"p-value: {result[1]:.4f}")
        for key, value in result[4].items():
            print(f"Critical Value ({key}): {value:.4f}")
        if result[1] < 0.05:
            print("Conclusion: Stationary (Reject Null Hypothesis)")
        else:
            print("Conclusion: Non-Stationary (Fail to Reject Null Hypothesis)")

    print_adf(df['CPI'], "Original CPI")

    # Differencing
    df['CPI_diff'] = df['CPI'].diff()
    print_adf(df['CPI_diff'], "Differenced CPI (1st Order)")

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['CPI_diff'], color='red', label='Differenced CPI')
    plt.title('1st Order Differenced CPI')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('plots/cpi_differenced.png')
    plt.close()
    print("Saved Differenced CPI plot.")

    # 3. ACF and PACF
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    plot_acf(df['CPI_diff'].dropna(), lags=48, ax=axes[0], title='ACF of Differenced CPI')
    plot_pacf(df['CPI_diff'].dropna(), lags=48, ax=axes[1], title='PACF of Differenced CPI')
    plt.tight_layout()
    plt.savefig('plots/acf_pacf.png')
    plt.close()
    print("Saved ACF/PACF plots.")

    # 4. Seasonal Decomposition
    decomposition = seasonal_decompose(df['CPI'], model='additive', period=12)
    fig = decomposition.plot()
    fig.set_size_inches(12, 8)
    plt.savefig('plots/seasonal_decomposition.png')
    plt.close()
    print("Saved Seasonal Decomposition plot.")
    
    print("\nEDA Pipeline completed successfully. All plots saved to 'plots/'.")

if __name__ == "__main__":
    run_eda()