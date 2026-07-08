import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_calibration_review_cli_writes_outputs(tmp_path: Path):
    summary_csv = tmp_path / "validation_summary.csv"
    output = tmp_path / "calibration_review_summary.csv"
    report = tmp_path / "calibration_review_report.txt"
    pd.DataFrame(
        [
            {
                "Scenario_ID": "eurusd_m5_period_1",
                "Status": "COMPLETED",
                "Symbol": "EURUSD",
                "Timeframe": "M5",
                "OHLC_Rows": 100,
            }
        ]
    ).to_csv(summary_csv, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_calibration_review.py",
            "--summary-csv",
            str(summary_csv),
            "--output",
            str(output),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "SQRE calibration review started" in result.stdout
    assert "Input summaries: 1" in result.stdout
    assert "Scenarios loaded: 1" in result.stdout
    assert output.exists()
    assert report.exists()


def test_run_calibration_review_cli_accepts_multiple_summary_inputs(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "calibration_review_summary.csv"
    report = tmp_path / "calibration_review_report.txt"
    pd.DataFrame([{"Scenario_ID": "one", "Status": "COMPLETED", "Symbol": "EURUSD", "Timeframe": "M5"}]).to_csv(
        first, index=False
    )
    pd.DataFrame([{"Scenario_ID": "two", "Status": "COMPLETED", "Symbol": "EURUSD", "Timeframe": "H1"}]).to_csv(
        second, index=False
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_calibration_review.py",
            "--summary-csv",
            str(first),
            "--summary-csv",
            str(second),
            "--output",
            str(output),
            "--report",
            str(report),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Input summaries: 2" in result.stdout
    assert pd.read_csv(output)["Scenario_ID"].tolist() == ["one", "two"]


def test_run_calibration_review_cli_fails_for_missing_input(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_calibration_review.py",
            "--summary-csv",
            str(tmp_path / "missing.csv"),
            "--output",
            str(tmp_path / "out.csv"),
            "--report",
            str(tmp_path / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Calibration review failed: Validation summary CSV not found" in result.stdout
