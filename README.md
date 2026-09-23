# BA26-04 Time Series | Forecasting Consumer Price Index (CPI) in Germany using ARIMA, ETS, and SARIMA

![Logo](./report/Images/General/banner.png "Project Logo")

## Project Overview

This project focuses on **forecasting Germany’s inflation using the Consumer Price Index (CPI)** as a univariate time series.

The primary objective is to **predict future CPI values** based on historical monthly data by modeling temporal dependencies such as trend and seasonality. The project applies classical time series methods to understand how past values influence future behavior and how well different models can generate reliable forecasts.

The analysis is strictly time-series-driven, involving:
- decomposition of the series into trend, seasonality, and residual components  
- transformation of data to achieve stationarity  
- identification of temporal structure using autocorrelation  

The goal is not only to produce forecasts, but to **compare how different time series models capture the underlying structure of inflation data**.

---

## Objectives

- forecast future inflation (CPI values) using historical time series data  
- identify and interpret trend and seasonal patterns in CPI  
- decompose the time series into meaningful components  
- test and ensure stationarity for model applicability  
- apply and compare three classical time series models:
  - ARIMA (AutoRegressive Integrated Moving Average)  
  - ETS (Error, Trend, Seasonality)  
  - SARIMA (Seasonal ARIMA)
- evaluate forecasting performance using appropriate regression metrics  
- demonstrate proper time series workflow from data preparation to model evaluation  

---

## Dataset

- **Source:** Destatis GENESIS Database  
- **Dataset Link:** https://www-genesis.destatis.de/datenbank/online/statistic/61111/table/61111-0002  
- **Table:** 61111-0002 (Consumer price index: Germany, months)  
- **Data Type:** univariate economic time series  
- **Frequency:** monthly observations  
- **Range:** 1991 – 2026 (~400+ data points)  

The dataset contains Germany’s Consumer Price Index (CPI), which measures the average change in prices of goods and services over time and is a standard indicator of inflation.

| Column | Description |
|--------|-------------|
| Date | Monthly time index |
| CPI | Consumer Price Index value |

## Dataset Description

We use Germany’s monthly Consumer Price Index (CPI) as a **univariate time series**, where each observation corresponds to a specific month.

### Data Structure

- each row represents one month  
- the primary variable is the CPI value  
- the time index is ordered chronologically from 1991 to 2026  

The dataset is evenly spaced with no irregular time gaps, making it suitable for classical time series modeling.

### Time Series Characteristics

The CPI series exhibits:

- **Trend:** a long-term upward movement reflecting inflation over time  
- **Seasonality:** mild repeating patterns across months (if present)  
- **Residual Component:** random fluctuations around the main structure  

These properties make the dataset suitable for decomposition and forecasting using classical time series methods.

### Prediction Target

| Target | Description | Models |
|--------|-------------|--------|
| **CPI** | Future CPI values (inflation level) | ARIMA, ETS, SARIMA |

The task is to forecast future CPI values based on past observations.

### Train-Test Split

- **Strategy:** chronological split to preserve temporal order  
- **Training Set:** earlier portion of data (e.g., 1991–2020)  
- **Test Set:** recent years (e.g., 2021–2026)  

Random splitting is avoided to prevent data leakage.

---

## Methodology

The methodology follows the **Knowledge Discovery in Databases (KDD)** process presented in the course. The time series workflow is mapped to KDD stages to ensure a structured and systematic approach.

```text
Database (Destatis CPI)
    |
    v
Data Selection --> Data Preprocessing --> Data Transformation --> Data Mining --> Models
      ^                   ^                      ^                     |
      |                   |                      |                     v
      +-------------------+----------------------+------ Evaluation & Interpretation
```


### 1. Problem Understanding

- define the application domain as **economic time series forecasting**  
- formulate the task as a **regression problem on temporal data**  
- specify the objective: forecast future CPI values using historical observations  
- define success criteria in terms of forecasting accuracy and model interpretability  

---

### 2. Database

- use Destatis GENESIS database as the data source  
- dataset: Germany Consumer Price Index (CPI), monthly frequency  
- identify CPI as the target variable representing inflation  
- document data characteristics such as time span (1991–2026) and frequency  

---

### 3. Data Selection

- select monthly CPI data for Germany from table 61111-0002  
- ensure consistent time intervals (monthly observations)  
- define a univariate time series for forecasting  
- exclude unnecessary attributes and retain only date and CPI  

---

### 4. Data Preprocessing

- load dataset from CSV format  
- convert date column to datetime format  
- set date as time index  
- ensure chronological ordering of observations  
- check and handle missing values if present  
- validate data consistency and integrity  

---

### 5. Data Transformation

- decompose the time series into:
  - trend  
  - seasonality  
  - residual  

- perform **Augmented Dickey-Fuller (ADF) test** to check stationarity  
- apply differencing if the series is non-stationary  
- analyze autocorrelation using ACF and PACF plots  
- split data chronologically into training and test sets  

---

### 6. Data Mining

This phase focuses on model development and comparison.

- **ARIMA:** models trend and autocorrelation after stationarity transformation  
- **ETS:** models level, trend, and seasonality directly  
- **SARIMA:** extends ARIMA to capture seasonal components 

Each model is trained on historical data and used to generate forecasts.

---

### 7. Evaluation and Verification

- evaluate models using RMSE, MAE, and MAPE  
- compare forecasting performance across models  
- assess model consistency and stability  
- verify whether model assumptions are satisfied  
- interpret results in terms of suitability for CPI forecasting  

---

### 8. Deployment Perspective

- discuss how CPI forecasts can support economic analysis and planning  
- describe how model outputs could be used for decision-making  
- note that deployment is conceptual within the scope of this project  

---

### 9. Monitoring and Maintenance Perspective

- recognize that CPI data evolves over time  
- models should be periodically retrained with new data  
- monitor model performance for degradation  
- treat forecasting as an iterative process requiring continuous updates  

## Evaluation Metrics

Since the objective is forecasting continuous values, regression-based metrics are used.

| Metric | Description |
|--------|-------------|
| **RMSE** | Root Mean Squared Error – penalizes larger errors more heavily |
| **MAE** | Mean Absolute Error – average absolute difference between actual and predicted values |
| **MAPE** | Mean Absolute Percentage Error – expresses error as a percentage |

### Why These Metrics?

- **RMSE** captures overall prediction error and penalizes large deviations  
- **MAE** provides a stable and interpretable average error  
- **MAPE** allows comparison in percentage terms, making results easier to interpret  

These metrics together provide a comprehensive evaluation of forecasting performance.

## Results

## 📊 Results (Example Structure)

| Model | RMSE | MAE | MAPE |
|------|------|------|------|
| ARIMA | TBD | TBD | TBD |
| ETS | TBD | TBD | TBD |
| SARIMA | TBD | TBD | TBD |

---

## Potential Delighters

The project can include additional enhancements beyond the core requirements to improve depth, robustness, and interpretability.

- **Forecast Confidence Intervals:**  
  Inclusion of prediction intervals to quantify uncertainty in forecasts and provide more realistic insights.

- **Structural Analysis of CPI:**  
  Identification of major shifts or anomalies (e.g., economic shocks) in the inflation series.


## Key Insights

- ARIMA provides a strong baseline for modeling trend and short-term dependencies but may struggle with seasonal effects  
- ETS performs well when trend and seasonality are clearly present and is often more interpretable  
- SARIMA improves upon ARIMA by incorporating seasonal structure, but may overfit if seasonality is weak  
- CPI data exhibits a strong trend and relatively low noise, making it well-suited for classical time series models  
- simpler models may perform as well as or better than more complex ones for structured economic data  

---

## Technology Stack

- Python  
- Pandas  
- NumPy  
- statsmodels (ARIMA, SARIMA)  
- statsmodels / Holt-Winters (ETS)  
- matplotlib  
- seaborn  

---

## Repository Structure

This repository follows the documentation-oriented structure used in the course.

- `Code/`
  - scripts for data loading, preprocessing, modeling, and evaluation  
- `LiteratureBIB/`
  - bibliography and literature references  
- `Manual/`
  - project manual (LaTeX)  
- `Poster/`
  - poster files  
- `Presentations/`
  - presentation slides  
- `ProjectManagement/`
  - planning documents  
- `report/`
  - main LaTeX report  
- `author.xlsx`
  - project metadata  

---

## Documentation Entry Points

- Report: `report/`  
- Manual: `Manual/`  
- Poster: `Poster/`  
- Presentations: `Presentations/`  

---

## Planned Workflow

- load and preprocess CPI data  
- perform exploratory analysis and decomposition  
- test for stationarity and apply transformations  
- train ARIMA, ETS, and SARIMA models  
- generate forecasts and evaluate performance  
- document findings and insights  

---

## Status

The project topic and methodological direction are defined as:

**Germany CPI Forecasting using ARIMA, ETS, and SARIMA, focusing on structured time series analysis and forecasting performance.**

Model results and final evaluation metrics will be added after implementation.
