"""!
@file modeling_pipeline.py
@author Siddhanth
@date 2026-04-27
@brief Time Series Modeling and Evaluation Pipeline

Trains ARIMA, ETS, and SARIMA models on the CPI data, evaluates 
them using hold-out testing, generates performance metrics 
(RMSE, MAE, MAPE), plots results, and serializes the models using joblib.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from data_loader import load_cpi_data
from models import ARIMAModel, ETSModelWrapper, SARIMAModel

PLOT_STYLES = {
    'ARIMA (1,1,1)': {'label': 'ARIMA Forecast', 'color': '#d62728'},
    'ETS (A,A,A)': {'label': 'ETS Forecast', 'color': '#2ca02c'},
    'SARIMA (1,1,1)x(1,1,1,12)': {'label': 'SARIMA Forecast', 'color': '#ff7f0e'},
}

def evaluate_models():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    plots_dir = os.path.join(base_dir, 'plots')
    models_dir = os.path.join(base_dir, 'saved_models')
    poster_images_dir = os.path.join(base_dir, '..', 'Poster', 'images')

    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(poster_images_dir, exist_ok=True)
    
    print("Loading data for modeling...")
    data_path = os.path.join(base_dir, 'data', '61111-0002_en.csv')
    df = load_cpi_data(filepath=data_path)
    
    # Train-test split (Let's hold out the last 24 months for testing)
    test_size = 24
    train, test = df.iloc[:-test_size], df.iloc[-test_size:]
    print(f"Training from {train.index.min().date()} to {train.index.max().date()} ({len(train)} months)")
    print(f"Testing from {test.index.min().date()} to {test.index.max().date()} ({len(test)} months)")
    
    models = {
        "ARIMA (1,1,1)": ARIMAModel(order=(1, 1, 1)),
        "ETS (A,A,A)": ETSModelWrapper(trend='add', seasonal='add', seasonal_periods=12),
        "SARIMA (1,1,1)x(1,1,1,12)": SARIMAModel(order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    }
    
    results = []
    predictions = {}
    
    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(14, 7),
        sharex=True,
        gridspec_kw={'height_ratios': [12, 1], 'hspace': 0.05}
    )
    fig.patch.set_alpha(0)
    ax_top.set_facecolor('none')
    ax_bottom.set_facecolor('none')

    for ax in (ax_top, ax_bottom):
        ax.plot(train.index, train['CPI'], label='Train Data', color='black')
        ax.plot(test.index, test['CPI'], label='Actual Test CPI', color='#1f77b4', linewidth=2, marker='o', markersize=5)
    
    print("\n--- Training Models ---")
    for name, model in models.items():
        print(f"Fitting {name}...")
        model.fit(train['CPI'])
        
        # Save model
        model_filename = os.path.join(models_dir, f"{name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '_')}.joblib")
        joblib.dump(model, model_filename)
        print(f"Saved {name} to {model_filename}")
        
        preds = model.predict(steps=test_size)
        predictions[name] = preds
        style = PLOT_STYLES[name]
        
        # Plotting predictions
        for ax in (ax_top, ax_bottom):
            ax.plot(test.index, preds, label=style['label'], color=style['color'], linestyle='--', linewidth=1.8)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(test['CPI'], preds))
        mae = mean_absolute_error(test['CPI'], preds)
        mape = mean_absolute_percentage_error(test['CPI'], preds) * 100
        
        results.append({
            "Model": name,
            "RMSE": round(rmse, 4),
            "MAE": round(mae, 4),
            "MAPE (%)": round(mape, 4)
        })
        
    ax_top.set_title("Germany CPI: Train vs Test vs Forecasts")
    ax_top.set_ylabel("CPI (2020=100)")
    ax_top.grid(True, alpha=0.3)
    ax_bottom.grid(True, alpha=0.3)
    ax_bottom.set_xlabel("Year")

    x_min = pd.to_datetime('2020-01-01')
    x_max = test.index.max() + pd.DateOffset(months=3)
    ax_top.set_xlim(x_min, x_max)
    ax_top.set_ylim(98, 135)
    ax_bottom.set_ylim(0, 5)
    ax_top.spines.bottom.set_visible(False)
    ax_bottom.spines.top.set_visible(False)
    ax_top.tick_params(labeltop=False)
    ax_bottom.xaxis.tick_bottom()
    ax_top.set_yticks([100, 110, 120, 130])
    ax_bottom.set_yticks([0])

    ax_top.legend(loc='upper left', fontsize=14)

    d = 0.008
    kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False, linewidth=1.2)
    ax_top.plot((-d, +d), (-d, +d), **kwargs)
    ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    kwargs.update(transform=ax_bottom.transAxes)
    ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    plt.tight_layout()

    forecast_plot_path = os.path.join(plots_dir, 'forecast_comparison.png')
    poster_plot_path = os.path.join(poster_images_dir, 'forecast_comparison.png')
    fig.savefig(forecast_plot_path, dpi=300, transparent=True, bbox_inches='tight')
    fig.savefig(poster_plot_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved '{forecast_plot_path}'.")
    print(f"Saved '{poster_plot_path}'.")

    fig_test, ax_test = plt.subplots(figsize=(14, 7))
    fig_test.patch.set_alpha(0)
    ax_test.set_facecolor('none')
    ax_test.plot(test.index, test['CPI'], label='Actual Test CPI', color='#1f77b4', linewidth=3, marker='o')

    for model_name, preds in predictions.items():
        style = PLOT_STYLES.get(model_name, {'label': f'{model_name} Forecast', 'color': 'gray'})
        ax_test.plot(test.index, preds, label=style['label'], color=style['color'], linestyle='--', linewidth=2.5)

    ax_test.set_title('German CPI: Test Period Forecast Comparison')
    ax_test.set_xlabel('Date')
    ax_test.set_ylabel('CPI (2020 = 100)')
    ax_test.legend(fontsize=16)
    ax_test.grid(True, alpha=0.2)

    plt.tight_layout()

    test_plot_path = os.path.join(plots_dir, 'test_forecast_comparison.png')
    poster_test_plot_path = os.path.join(poster_images_dir, 'test_forecast_comparison.png')
    fig_test.savefig(test_plot_path, dpi=300, transparent=True, bbox_inches='tight')
    fig_test.savefig(poster_test_plot_path, dpi=300, transparent=True, bbox_inches='tight')
    plt.close(fig_test)
    print(f"Saved '{test_plot_path}'.")
    print(f"Saved '{poster_test_plot_path}'.")
    
    # Export Results Table
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(plots_dir, 'evaluation_metrics.csv'), index=False)
    
    print("\n--- Evaluation Metrics ---")
    print(results_df.to_string(index=False))
    
    # LaTeX Export
    latex_table = results_df.to_latex(index=False, caption="Model Evaluation Metrics", label="tab:evaluation")
    with open(os.path.join(plots_dir, 'evaluation_metrics.tex'), 'w') as f:
        f.write(latex_table)
    print("\nSaved LaTeX table to 'plots/evaluation_metrics.tex'.")

if __name__ == "__main__":
    evaluate_models()
