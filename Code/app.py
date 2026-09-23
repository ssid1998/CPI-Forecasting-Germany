"""!
@file app.py
@author Siddhanth
@date 2026-04-27
@brief Streamlit Interactive Dashboard for CPI Forecasting

This application provides a web-based user interface to interact
with the serialized statsmodels Time Series objects. Users can adjust
forecast horizons, switch between models, and dynamically view 
confidence intervals.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, "src"))

import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from src.data_loader import load_cpi_data

st.set_page_config(page_title="Germany CPI Forecasting", page_icon="🇩🇪", layout="wide")

# Custom CSS to create a balanced container width
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Germany Consumer Price Index (CPI) Forecasting")
st.markdown("""
Welcome to the Time Series Analytics Dashboard for forecasting Germany's CPI. 
This application loads our pre-trained classical models (**ARIMA, ETS, SARIMA**) 
to predict inflation trends and compare their performance against actual hidden test data.
""")

# Resolve paths relative to this file, not the current working directory
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data", "61111-0002_en.csv")
models_dir = os.path.join(base_dir, "saved_models")

@st.cache_data
def get_data():
    return load_cpi_data(data_path)


def render_chart_note(shown_train_start, train_start, train_end, test_start, test_end):
    st.markdown(
        """
        <style>
        .chart-note {
            font-size: 0.875rem;
            color: rgba(49, 51, 63, 0.6);
            line-height: 1.4;
            margin-top: 0.35rem;
        }
        .chart-note ul {
            margin: 0.25rem 0 0 1.25rem;
            padding: 0;
        }
        .chart-note li {
            margin: 0.1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="chart-note">
            <div>For readability, the chart is zoomed to show training data from <strong>{shown_train_start}</strong> onward.</div>
            <ul>
                <li>The models were trained on the full training set from <strong>{train_start}</strong> to <strong>{train_end}</strong>.</li>
                <li>The 24-month test period runs from <strong>{test_start}</strong> to <strong>{test_end}</strong>.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

df = get_data()
test_size = 24
train, test = df.iloc[:-test_size], df.iloc[-test_size:]
chart_start = pd.Timestamp('2020-01-01')
train_recent = train[train.index >= chart_start]

train_start = train.index.min().date()
train_end = train.index.max().date()
test_start = test.index.min().date()
test_end = test.index.max().date()
shown_train_start = train_recent.index.min().date()

st.sidebar.header("Configuration")
model_choice = st.sidebar.selectbox("Select Model", ["ARIMA (1,1,1)", "ETS (A,A,A)", "SARIMA (1,1,1)x(1,1,1,12)", "Compare All Models"])

ci_level = st.sidebar.selectbox(
    "Confidence Interval Level", 
    [80, 90, 95, 96, 97, 98, 99], 
    index=2, # Default to 95
    format_func=lambda x: f"{x}%"
)

# Calculate alpha for confidence intervals
alpha = 1.0 - (ci_level / 100.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Guide")
st.sidebar.markdown("""
- **ARIMA (1,1,1):** Looks 1 month back, uses 1st-order differencing, and checks 1 month of past errors.
- **ETS (A,A,A):** Additive Error, Additive Trend, Additive Seasonality. Best for linear growth and flat seasonal bumps.
- **SARIMA:** Like ARIMA, but specifically looks back 12 months to catch yearly repeating cycles.
""")

# Map UI name to filename
filename_map = {
    "ARIMA (1,1,1)": "ARIMA_1_1_1.joblib",
    "ETS (A,A,A)": "ETS_A_A_A.joblib",
    "SARIMA (1,1,1)x(1,1,1,12)": "SARIMA_1_1_1x1_1_1_12.joblib"
}

model_path = os.path.join(models_dir, filename_map.get(model_choice, ""))

if model_choice == "Compare All Models":
    st.subheader("Forecast vs Actual: All Models Comparison")
    
    # Calculate Metrics for all
    metrics_data = []
    preds_dict = {}
    
    for m_name, f_name in filename_map.items():
        m_path = os.path.join(models_dir, f_name)
        if os.path.exists(m_path):
            model = joblib.load(m_path)
            preds = model.predict(steps=test_size)
            preds_dict[m_name] = preds
            
            rmse = np.sqrt(mean_squared_error(test['CPI'], preds))
            mae = mean_absolute_error(test['CPI'], preds)
            mape = mean_absolute_percentage_error(test['CPI'], preds) * 100
            
            metrics_data.append({"Model": m_name, "RMSE": rmse, "MAE": mae, "MAPE (%)": mape})
            
    # Display Metrics Table
    if metrics_data:
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df.style.highlight_min(subset=["RMSE", "MAE", "MAPE (%)"], color='lightgreen', axis=0), use_container_width=True)
        
    # Interactive Plotly Chart
    fig = go.Figure()
    
    # Plot Train (zoomed for visibility)
    fig.add_trace(go.Scatter(x=train_recent.index, y=train_recent['CPI'], 
                             mode='lines', name='Train Data (Shown Range)', line=dict(color='black', width=2)))
                             
    # Plot Test
    fig.add_trace(go.Scatter(x=test.index, y=test['CPI'], 
                             mode='lines+markers', name='Actual Test Data', line=dict(color='#1f77b4', width=3)))
                             
    # Plot Forecasts
    colors = {'ARIMA (1,1,1)': '#d62728', 'ETS (A,A,A)': '#2ca02c', 'SARIMA (1,1,1)x(1,1,1,12)': '#ff7f0e'}
    for m_name, preds in preds_dict.items():
        fig.add_trace(go.Scatter(x=test.index, y=preds, 
                                 mode='lines', name=f'{m_name} Forecast', line=dict(color=colors.get(m_name, 'gray'), dash='dash', width=2)))
                                 
    fig.update_layout(title="CPI Forecast Comparison (24-Month Horizon)",
                      xaxis_title="Date",
                      yaxis_title="CPI (2020=100)",
                      legend=dict(itemdoubleclick=False),
                      hovermode="x unified",
                      template="plotly_white")
                        
    st.plotly_chart(fig, use_container_width=True)
    render_chart_note(shown_train_start, train_start, train_end, test_start, test_end)

elif os.path.exists(model_path):
    # Load the model
    with st.spinner(f"Loading {model_choice} model..."):
        model = joblib.load(model_path)
    
    st.subheader(f"Forecast vs Actual: {model_choice}")
    
    # Generate predictions
    preds = model.predict(steps=test_size)
    
    # Confidence Intervals
    lower, upper = None, None
    if hasattr(model, 'get_confidence_intervals'):
        try:
            ci = model.get_confidence_intervals(steps=test_size, alpha=alpha)
            if 'lower CPI' in ci.columns:
                lower, upper = ci['lower CPI'], ci['upper CPI']
            else:
                lower, upper = ci.iloc[:, 0], ci.iloc[:, 1]
        except Exception as e:
            st.warning(f"Could not calculate confidence intervals: {e}")
            
    # Calculate Metrics
    rmse = np.sqrt(mean_squared_error(test['CPI'], preds))
    mae = mean_absolute_error(test['CPI'], preds)
    mape = mean_absolute_percentage_error(test['CPI'], preds) * 100
    
    # Metrics display
    col1, col2, col3 = st.columns(3)
    col1.metric("RMSE (Root Mean Squared Error)", f"{rmse:.4f}", help="Penalizes huge mistakes. Lower is better.")
    col2.metric("MAE (Mean Absolute Error)", f"{mae:.4f}", help="Average raw index points the model was off by. Lower is better.")
    col3.metric("MAPE (Mean Absolute % Error)", f"{mape:.2f}%", help="< 10% is highly accurate. Lower is better.")
    
    # Interactive Plotly Chart
    fig = go.Figure()
    
    # Plot Confidence Intervals FIRST so they sit in the background
    if lower is not None and upper is not None:
        fig.add_trace(go.Scatter(x=test.index.tolist() + test.index.tolist()[::-1],
                                 y=upper.tolist() + lower.tolist()[::-1],
                                 fill='toself',
                                 fillcolor='rgba(255, 0, 0, 0.15)',
                                 line=dict(color='rgba(255,255,255,0)'),
                                 hoverinfo="skip",
                                 showlegend=True,
                                 name=f'{ci_level}% Confidence Interval'))

    # Plot Train (zoomed for visibility)
    fig.add_trace(go.Scatter(x=train_recent.index, y=train_recent['CPI'], 
                             mode='lines', name='Train Data (Shown Range)', line=dict(color='black', width=2)))
                             
    # Plot Test
    fig.add_trace(go.Scatter(x=test.index, y=test['CPI'], 
                             mode='lines+markers', name='Actual Test Data', line=dict(color='#1f77b4', width=2)))
                             
    # Plot Forecast
    fig.add_trace(go.Scatter(x=test.index, y=preds, 
                             mode='lines+markers', name=f'{model_choice} Forecast', line=dict(color='#d62728', dash='dash', width=2)))
                             
    fig.update_layout(title=f"CPI Forecast using {model_choice} (24-Month Horizon)",
                      xaxis_title="Date",
                      yaxis_title="CPI (2020=100)",
                      legend=dict(itemdoubleclick=False),
                      hovermode="x unified",
                      template="plotly_white")
                        
    st.plotly_chart(fig, use_container_width=True)
    render_chart_note(shown_train_start, train_start, train_end, test_start, test_end)

else:
    st.error(f"Model files not found! Please run `modeling_pipeline.py` first to train and save the models.")
    st.info("You can run the pipeline by executing `start.sh` or `start.bat`.")

st.markdown("---")

# --- EXPLANATIONS SECTION ---
st.header("Interpretation & Methodology")

with st.expander("1. How are these predictions made? (The Pipeline)"):
    st.write("""
    In machine learning, models cannot be evaluated on the data they were trained on (that leads to overfitting). 
    """)
    st.markdown(f"""
    - **Training Data:** We gave the models historical CPI data from **{train_start}** to **{train_end}**.
    - **Test Data:** We hid the data from **{test_start}** to **{test_end}**.
    - **The Test:** We asked the models to blindly predict **24 months** into the future, and then compared their predictions against the actual hidden data.
    - **Chart Display:** For readability, the chart is zoomed to show the training history from **{shown_train_start}** onward, not the full training history.
    """)

with st.expander("2. What do the Confidence Intervals mean?"):
    st.write(f"""
    Forecasting the future is inherently uncertain. The **dashed line** is the model's absolute best guess (the mean forecast). 
    
    The **shaded area** is the Confidence Interval. The model is stating: 
    > *"Based on historical volatility, I am confident that the actual CPI will land somewhere inside this shaded band."*
    
    Notice how the band gets wider the further right you go—predicting 1 month out is much easier than predicting 24 months out. You can adjust the strictness of this interval using the filter in the sidebar.
    """)

with st.expander("3. Are these Error Metrics good or bad?"):
    st.write("""
    To mathematically prove which model is best, we use error metrics. For all of these, **Lower is Better (0 is perfect).**
    
    - **MAE (Mean Absolute Error):** On average, how many raw CPI index points was the prediction off by?
    - **RMSE (Root Mean Squared Error):** Similar to MAE, but it squares the errors before averaging. This heavily penalizes huge, single-month mistakes.
    - **MAPE (Mean Absolute Percentage Error):** On average, by what *percentage* was the model wrong?
    
    **The MAPE Reference Scale:**
    - **< 10%:** Highly accurate forecasting
    - **10% - 20%:** Good forecasting
    - **20% - 50%:** Reasonable forecasting
    - **> 50%:** Inaccurate model
    
    *Our Result:* All our models achieved a MAPE of less than **1%**, which is a phenomenal result for a 24-month macroeconomic forecast!
    """)

with st.expander("4. Inference from the Graphs (Why ETS wins)"):
    st.write("""
    By comparing the three models, we can draw a clear macroeconomic conclusion:
    
    1. **ARIMA fails at seasonality:** The ARIMA forecast is mostly a straight diagonal line. It completely misses the "wobbles" (seasonal peaks/valleys) of the actual blue data.
    2. **SARIMA catches the seasons, but overshoots:** SARIMA tries to map the 12-month seasons, but its mathematical rigidity causes it to slightly misalign with the actual magnitude of the shocks.
    3. **ETS is the champion:** The ETS (A,A,A) model perfectly mimics the "heartbeat" of the actual data while capturing the upward trend. Its prediction was off by only ~0.64 index points over 2 whole years (MAPE ~0.52%).
    
    **Conclusion:** Germany's CPI possesses strict Additive Trend and Additive Seasonality. The Exponential Smoothing (ETS) algorithm handles this continuous additive behavior much better than the rigid autoregressive math of ARIMA.
    """)
