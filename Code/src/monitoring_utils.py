"""!
@file monitoring_utils.py
@author Siddhanth
@date 2026-05-17
@brief Monitoring Utilities for the CPI Forecasting Pipeline

Provides data validation, artifact verification, metric drift detection,
and JSON report generation to ensure the repository remains healthy
and reproducible over time.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, UTC

import pandas as pd

from data_loader import load_cpi_data


EXPECTED_MODEL_FILES = [
    "ARIMA_1_1_1.joblib",
    "ETS_A_A_A.joblib",
    "SARIMA_1_1_1x1_1_1_12.joblib",
]

EXPECTED_PLOT_FILES = [
    "evaluation_metrics.csv",
    "evaluation_metrics.tex",
    "forecast_comparison.png",
    "test_forecast_comparison.png",
]

METRIC_COLUMNS = ["RMSE", "MAE", "MAPE (%)"]


@dataclass
class MonitoringResult:
    name: str
    passed: bool
    details: str


def validate_cpi_series(data_path: str) -> list[MonitoringResult]:
    results: list[MonitoringResult] = []
    if not os.path.exists(data_path):
        return [MonitoringResult("data_file_exists", False, f"Missing CPI file: {data_path}")]

    df = load_cpi_data(filepath=data_path)
    results.append(MonitoringResult("data_file_exists", True, f"Loaded {len(df)} rows from {data_path}"))

    results.append(MonitoringResult("series_non_empty", not df.empty, "CPI series must contain at least one observation."))

    has_datetime_index = isinstance(df.index, pd.DatetimeIndex)
    results.append(MonitoringResult("datetime_index", has_datetime_index, "CPI series must use a DatetimeIndex."))

    has_monthly_frequency = getattr(df.index, "freqstr", None) == "MS"
    results.append(MonitoringResult("monthly_frequency", has_monthly_frequency, "CPI series must have strict month-start frequency (MS)."))

    duplicates = int(df.index.duplicated().sum()) if has_datetime_index else math.inf
    results.append(MonitoringResult("no_duplicate_dates", duplicates == 0, f"Duplicate dates detected: {duplicates}"))

    missing_values = int(df["CPI"].isna().sum()) if "CPI" in df.columns else math.inf
    results.append(MonitoringResult("no_missing_cpi", missing_values == 0, f"Missing CPI values detected: {missing_values}"))

    is_numeric = pd.api.types.is_numeric_dtype(df["CPI"]) if "CPI" in df.columns else False
    results.append(MonitoringResult("numeric_cpi", is_numeric, "CPI column must remain numeric after loading."))

    return results


def run_command(name: str, command: list[str], cwd: str) -> MonitoringResult:
    try:
        completed = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    except Exception as exc:  # pragma: no cover - defensive
        return MonitoringResult(name, False, f"Failed to start command {command!r}: {exc}")

    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        return MonitoringResult(name, False, details)

    details = completed.stdout.strip().splitlines()
    summary = details[-1] if details else "Command completed successfully."
    return MonitoringResult(name, True, summary)


def verify_required_artifacts(base_dir: str) -> list[MonitoringResult]:
    models_dir = os.path.join(base_dir, "saved_models")
    plots_dir = os.path.join(base_dir, "plots")
    results: list[MonitoringResult] = []

    for filename in EXPECTED_MODEL_FILES:
        path = os.path.join(models_dir, filename)
        results.append(MonitoringResult(f"artifact_model_{filename}", os.path.exists(path), f"Expected model artifact: {path}"))

    for filename in EXPECTED_PLOT_FILES:
        path = os.path.join(plots_dir, filename)
        results.append(MonitoringResult(f"artifact_plot_{filename}", os.path.exists(path), f"Expected plot/report artifact: {path}"))

    return results


def load_metrics_table(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    expected_columns = ["Model", *METRIC_COLUMNS]
    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Metrics file {csv_path} is missing columns: {missing}")
    return df[expected_columns].copy()


def compare_metrics_against_baseline(current_csv: str, baseline_csv: str, threshold_pct: float) -> list[MonitoringResult]:
    if not os.path.exists(current_csv):
        return [MonitoringResult("metrics_file_present", False, f"Current metrics file missing: {current_csv}")]

    if not os.path.exists(baseline_csv):
        return [MonitoringResult("metrics_baseline_present", True, f"No baseline metrics found at {baseline_csv}; comparison skipped.")]

    current_df = load_metrics_table(current_csv).set_index("Model")
    baseline_df = load_metrics_table(baseline_csv).set_index("Model")
    results: list[MonitoringResult] = []

    common_models = sorted(set(current_df.index) & set(baseline_df.index))
    if not common_models:
        return [MonitoringResult("metrics_comparable", False, "No overlapping model names between current and baseline metrics.")]

    threshold_fraction = threshold_pct / 100.0
    for model in common_models:
        for metric in METRIC_COLUMNS:
            baseline_value = float(baseline_df.loc[model, metric])
            current_value = float(current_df.loc[model, metric])
            allowed = baseline_value * (1.0 + threshold_fraction)
            passed = current_value <= allowed
            details = (
                f"{model} {metric}: current={current_value:.4f}, baseline={baseline_value:.4f}, "
                f"allowed_max={allowed:.4f} ({threshold_pct:.1f}% threshold)"
            )
            results.append(MonitoringResult(f"metric_drift_{model}_{metric}", passed, details))

    return results


def save_metrics_baseline(current_csv: str, baseline_csv: str) -> None:
    os.makedirs(os.path.dirname(baseline_csv), exist_ok=True)
    shutil.copyfile(current_csv, baseline_csv)


def write_monitoring_report(report_path: str, results: list[MonitoringResult]) -> None:
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    payload = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "passed": all(result.passed for result in results),
        "results": [asdict(result) for result in results],
    }
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def monitoring_cli(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the CPI monthly monitoring workflow.")
    parser.add_argument("--base-dir", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    parser.add_argument("--threshold-pct", type=float, default=15.0, help="Allowed metric increase versus baseline before failure.")
    parser.add_argument("--accept-baseline", action="store_true", help="Replace the stored metric baseline with the newly generated metrics.")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--skip-eda", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    args = parser.parse_args(argv)

    base_dir = os.path.abspath(args.base_dir)
    data_path = os.path.join(base_dir, "data", "61111-0002_en.csv")
    monitoring_dir = os.path.join(base_dir, "monitoring")
    baseline_csv = os.path.join(monitoring_dir, "baseline_metrics.csv")
    latest_report = os.path.join(monitoring_dir, "latest_monitoring_report.json")
    current_metrics = os.path.join(base_dir, "plots", "evaluation_metrics.csv")

    results: list[MonitoringResult] = []
    results.extend(validate_cpi_series(data_path))

    if not args.skip_tests:
        results.append(run_command(
            "pytest_monitoring_suite",
            [sys.executable, "-m", "pytest", "tests/test_data_loader.py", "tests/test_models.py", "tests/test_monitoring_workflow.py", "-v"],
            cwd=base_dir,
        ))

    if not args.skip_eda:
        results.append(run_command("eda_pipeline", [sys.executable, "src/eda_pipeline.py"], cwd=base_dir))

    if not args.skip_train:
        results.append(run_command("modeling_pipeline", [sys.executable, "src/modeling_pipeline.py"], cwd=base_dir))

    results.extend(verify_required_artifacts(base_dir))
    results.extend(compare_metrics_against_baseline(current_metrics, baseline_csv, args.threshold_pct))

    if args.accept_baseline and os.path.exists(current_metrics):
        save_metrics_baseline(current_metrics, baseline_csv)
        results.append(MonitoringResult("baseline_updated", True, f"Stored baseline metrics at {baseline_csv}"))

    write_monitoring_report(latest_report, results)
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(monitoring_cli())
