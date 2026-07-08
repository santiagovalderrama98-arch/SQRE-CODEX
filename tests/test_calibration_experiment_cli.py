import subprocess
import sys
from pathlib import Path

import pandas as pd


def _write_config(path: Path, ohlc_path: Path) -> None:
    path.write_text(
        f"""
experiment_name: calibration_experiments_v1
symbol: EURUSD
pip_size: 0.0001
forward_candles: [3, 6, 12]
base_scenarios:
  - scenario_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    ohlc_path: {ohlc_path}
duration_experiments:
  - experiment_id: duration_baseline
    max_structure_duration_seconds:
      H4: 604800
sample_size_experiments:
  - experiment_id: sample_size_5
    minimum_sample_size: 5
""",
        encoding="utf-8",
    )


def test_calibration_experiment_cli_non_strict_missing_input_writes_outputs(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    summary_csv = tmp_path / "summary.csv"
    report = tmp_path / "report.txt"
    _write_config(config_path, tmp_path / "missing.csv")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_calibration_experiments.py",
            "--config",
            str(config_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--summary-csv",
            str(summary_csv),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "SQRE calibration experiments started" in result.stdout
    assert "Experiment runs configured: 2" in result.stdout
    assert summary_csv.exists()
    assert report.exists()
    assert set(pd.read_csv(summary_csv)["Status"]) == {"MISSING_INPUT"}


def test_calibration_experiment_cli_parses_filters(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    summary_csv = tmp_path / "summary.csv"
    report = tmp_path / "report.txt"
    _write_config(config_path, tmp_path / "missing.csv")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_calibration_experiments.py",
            "--config",
            str(config_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--summary-csv",
            str(summary_csv),
            "--report",
            str(report),
            "--experiment-type",
            "DURATION",
            "--scenario",
            "eurusd_h4_period_1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Experiment runs selected: 1" in result.stdout
    assert pd.read_csv(summary_csv)["Experiment_Type"].tolist() == ["DURATION"]


def test_calibration_experiment_cli_strict_missing_input_returns_nonzero(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    _write_config(config_path, tmp_path / "missing.csv")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_calibration_experiments.py",
            "--config",
            str(config_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--summary-csv",
            str(tmp_path / "summary.csv"),
            "--report",
            str(tmp_path / "report.txt"),
            "--strict",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Calibration experiments failed" in result.stdout
