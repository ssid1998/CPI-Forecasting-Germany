"""!
@file test.py
@author Siddhanth
@date 2026-05-17
@brief Scratchpad for External Data Fetching

Utility script that fetches Germany CPI data from the FRED database
using pandas_datareader. Not part of the main pipeline; used for
quick external validation only.
"""

from pandas_datareader import data as pdr

df = pdr.DataReader('DEUCPIALLMINMEI', 'fred')
df.show()