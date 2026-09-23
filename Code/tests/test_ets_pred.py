"""!
@file test_ets_pred.py
@author Siddhanth
@date 2026-05-17
@brief ETS Prediction Sanity Check

Standalone script that loads the CPI dataset, fits an ETS(A,A,A) model,
and prints the 24-month point forecasts and prediction intervals using
the underlying statsmodels get_prediction API.
"""

import pandas as pd
from src.data_loader import load_cpi_data
from src.models import ETSModelWrapper

df = load_cpi_data()
train = df.iloc[:-24]
model = ETSModelWrapper(trend='add', seasonal='add', seasonal_periods=12)
model.fit(train['CPI'])
res = model.model_fit.get_prediction(start=len(train), end=len(train)+23)
ci = res.pred_int(alpha=0.05)
print(ci)
