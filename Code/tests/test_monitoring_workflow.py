"""!
@file test_monitoring_workflow.py
@author Siddhanth
@date 2026-05-17
@brief Integration Tests for the Monitoring Workflow

Validates that the monitoring utilities correctly detect missing artifacts,
validate the CPI dataset, and flag metric drift when current model
performance deviates from the stored baseline.
"""

import os
import sys

import pandas as pd


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from monitoring_utils import (  # noqa: E402
    compare_metrics_against_baseline,
    save_metrics_baseline,
    validate_cpi_series,
    verify_required_artifacts,
)


def test_validate_cpi_series_real_dataset():
    results = validate_cpi_series(os.path.join(BASE_DIR, "data", "61111-0002_en.csv"))
    assert results, "Monitoring data validation should return checks."
    assert all(result.passed for result in results), "The committed CPI dataset should pass monitoring validation checks."


def test_verify_required_artifacts_current_repo_state():
    results = verify_required_artifacts(BASE_DIR)
    assert results, "Artifact verification should produce checks."
    assert all(result.passed for result in results), "Saved models and monitoring artifacts should exist after the committed pipeline outputs."


def test_compare_metrics_against_baseline_detects_drift(tmp_path):
    current_csv = os.path.join(BASE_DIR, "plots", "evaluation_metrics.csv")
    baseline_csv = tmp_path / "baseline_metrics.csv"

    save_metrics_baseline(current_csv, str(baseline_csv))

    modified_df = pd.read_csv(current_csv)
    modified_df.loc[modified_df["Model"] == "ETS (A,A,A)", "RMSE"] *= 1.50
    drifted_csv = tmp_path / "drifted_metrics.csv"
    modified_df.to_csv(drifted_csv, index=False)

    results = compare_metrics_against_baseline(str(drifted_csv), str(baseline_csv), threshold_pct=10.0)
    assert any(not result.passed for result in results), "A strong metric increase should be flagged as monitoring drift."
