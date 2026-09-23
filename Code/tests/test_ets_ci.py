"""!
@file test_ets_ci.py
@author Siddhanth
@date 2026-05-17
@brief ETS Confidence Interval Sanity Check

Standalone script that loads the CPI dataset, fits an ETS(A,A,A) model,
and prints the 24-month prediction intervals to verify that the
get_confidence_intervals method returns sensible bounds.
"""

import pandas as pd
from src.data_loader import load_cpi_data
from src.models import ETSModelWrapper
import numpy as np

df = load_cpi_data()
train = df.iloc[:-24]
model = ETSModelWrapper(trend='add', seasonal='add', seasonal_periods=12)
model.fit(train['CPI'])
ci = model.get_confidence_intervals(24)
print("CI:")
print(ci.head())
preds = model.predict(24)
print("PREDS:")
print(preds.head())
