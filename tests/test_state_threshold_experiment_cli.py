from __future__ import annotations

import subprocess
import sys


def _write_config(path, missing_ohlc_path) -> None:
    path.write_text(
        f"""
experiment_name: cli_state_thresholds
symbol: EURUSD
pip_size: 0.0001
forward_candles: [3]
minimum_sample_size: 5
baseline_max_structure_duration_seconds:
  H4: 604800
state_config_path: configs/validation/state_threshold_profiles.yaml
base_scenarios:
  - scenario_id: eurusd_h4_period_1
    symbol: EURUSD
    timeframe: H4
    ohlc_path: {missing_ohlc_path}
profiles:
  - state_baseline
  - directional_stricter
""",
        encoding="utf-8",
    )


def test_state_threshold_experiment_cli_writes_missing_input_summary(tmp_path) -> None:
    config = tmp_path / "config.yaml"
    summary = tmp_path / "summary.csv"
    report = tmp_path / "report.txt"
    _write_config(config, tmp_path / "missing.csv")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_state_threshold_experiments.py",
            "--config",
            str(config),
            "--output-dir",
            str(tmp_path / "validation"),
            "--summary-csv",
            str(summary),
            "--report",
            str(report),
            "--profile",
            "directional_stricter",
            "--scenario",
            "eurusd_h4_period_1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "SQRE state threshold experiments started" in completed.stdout
    assert "Runs selected: 1" in completed.stdout
    assert "Status: MISSING_INPUT" in completed.stdout
    assert summary.exists()
    assert report.exists()


def test_state_threshold_experiment_cli_strict_returns_nonzero_for_missing_input(tmp_path) -> None:
    config = tmp_path / "config.yaml"
    _write_config(config, tmp_path / "missing.csv")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_state_threshold_experiments.py",
            "--config",
            str(config),
            "--output-dir",
            str(tmp_path / "validation"),
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

    assert completed.returncode == 1
    assert "State threshold experiments failed" in completed.stdout
