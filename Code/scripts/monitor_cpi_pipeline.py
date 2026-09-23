#!/usr/bin/env python3
"""!
@file monitor_cpi_pipeline.py
@author Siddhanth
@date 2026-05-17
@brief Monthly Monitoring Entrypoint

Command-line interface that orchestrates the full monitoring workflow:
validates the CPI dataset, runs pytest suites, executes EDA and modeling
pipelines, verifies artifact presence, and compares current metrics against
a stored baseline. Results are written as a JSON monitoring report.
"""

import os
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from monitoring_utils import monitoring_cli


if __name__ == "__main__":
    raise SystemExit(monitoring_cli())
