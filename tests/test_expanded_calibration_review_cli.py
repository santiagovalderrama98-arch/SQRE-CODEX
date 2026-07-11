import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_expanded_calibration_review_cli_writes_outputs(tmp_path: Path):
    summary_csv = tmp_path / "expanded_summary.csv"
    output = tmp_path / "expanded_calibration_review_summary.csv"
    report = tmp_path / "expanded_calibration_review_report.txt"
    pd.DataFrame([_row("eurusd_h4_period_1", "H4"), _row("eurusd_h4_period_2", "H4")]).to_csv(
        summary_csv, index=False
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_expanded_calibration_review.py",
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
    assert "SQRE expanded historical calibration review started" in result.stdout
    assert "Rows loaded: 2" in result.stdout
    assert "Timeframes reviewed: 1" in result.stdout
    assert output.exists()
    assert report.exists()


def test_run_expanded_calibration_review_cli_accepts_multiple_summary_inputs(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "expanded_calibration_review_summary.csv"
    report = tmp_path / "expanded_calibration_review_report.txt"
    pd.DataFrame([_row("one", "M5")]).to_csv(first, index=False)
    pd.DataFrame([_row("two", "H1")]).to_csv(second, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_expanded_calibration_review.py",
            "--summary-csv",
            str(first),
            "--summary-csv",
            str(second),
            "--output",
            str(output),
            "--report",
            str(report),
            "--high-low-sample-threshold",
            "40",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Input summaries: 2" in result.stdout
    assert set(pd.read_csv(output)["Timeframe"]) == {"M5", "H1"}


def test_run_expanded_calibration_review_cli_fails_for_missing_input(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_expanded_calibration_review.py",
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
    assert "Expanded historical calibration review failed: Expanded historical summary CSV not found" in result.stdout


def _row(scenario_id: str, timeframe: str) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
        "OHLC_Rows": 1000,
        "Structures_Detected": 10,
        "Average_Structure_Duration": 3600,
        "States_Generated": 10,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Directional_Displacement_Count": 4,
        "Directional_Expansion_Count": 2,
        "Volatile_Rotation_Count": 1,
        "Complex_Consolidation_Count": 2,
        "Low_Quality_Structure_Count": 0,
        "Unclassified_Count": 0,
        "Average_Forward_Range_Pips": 25,
        "Average_Outcome_Magnitude_Pips": 10,
        "Direction_Alignment_Rate": 0.55,
        "Low_Sample_Conditions_Research": 4,
        "Low_Sample_Conditions_Price_Outcome": 3,
    }
