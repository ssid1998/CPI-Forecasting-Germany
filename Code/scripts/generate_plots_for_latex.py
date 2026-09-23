"""!
@file generate_plots_for_latex.py
@author Siddhanth
@date 2026-05-17
@brief EDA Plot Generator for LaTeX Reports

Generates differencing, ACF/PACF, and seasonal decomposition plots
from the Destatis CPI dataset and saves them to Code/plots/ for inclusion
in the project report and poster.
"""

import os
import sys
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose

# Ensure the src module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_loader import load_cpi_data

def generate_plots():
    # Load data
    data_path = '../Code/data/61111-0002_en.csv' if os.path.exists('../Code/data/61111-0002_en.csv') else 'data/61111-0002_en.csv'
    df = load_cpi_data(filepath=data_path)
    ts = df['CPI'].dropna()
    
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # 1. Differencing Plot (ARIMA)
    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    axes[0].plot(ts)
    axes[0].set_title('Original CPI Series (Non-Stationary)')
    axes[0].set_ylabel('CPI')
    axes[1].plot(ts.diff().dropna())
    axes[1].set_title('First-Differenced CPI Series (Stationary)')
    axes[1].set_ylabel('Diff(CPI)')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'differencing.png'), dpi=300)
    plt.close()
    
    # 2. ACF / PACF Plot (ARIMA/SARIMA)
    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    sm.graphics.tsa.plot_acf(ts.diff().dropna(), lags=40, ax=axes[0], title="Autocorrelation (ACF) of Differenced CPI")
    sm.graphics.tsa.plot_pacf(ts.diff().dropna(), lags=40, ax=axes[1], title="Partial Autocorrelation (PACF) of Differenced CPI")
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'acf_pacf.png'), dpi=300)
    plt.close()
    
    # 3. Seasonal Decomposition Plot (ETS) - Custom aligned Y-labels
    decomposition = seasonal_decompose(ts, model='additive', period=12)
    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    
    axes[0].plot(decomposition.observed, color='black')
    axes[0].set_ylabel('CPI')
    
    axes[1].plot(decomposition.trend, color='blue')
    axes[1].set_ylabel('Trend')
    
    axes[2].plot(decomposition.seasonal, color='green')
    axes[2].set_ylabel('Seasonal')
    
    axes[3].plot(decomposition.resid, color='red')
    axes[3].set_ylabel('Residual')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'decomposition.png'), dpi=300)
    plt.close()

    print("Plots generated successfully in Code/plots/")

if __name__ == '__main__':
    generate_plots()