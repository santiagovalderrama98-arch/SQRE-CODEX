import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_timeframe_duration_calibration_review_cli_works_with_synthetic_csv(tmp_path: Path):
    summary = tmp_path / "experiment_summary.csv"
    output = tmp_path / "review_summary.csv"
    report = tmp_path / "review_report.txt"
    pd.DataFrame([_row("one", "M5", "m5_duration_4h_baseline")]).to_csv(summary, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_timeframe_duration_calibration_review.py",
            "--experiment-summary",
            str(summary),
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
    assert "SQRE H1/M5 duration calibration review started" in result.stdout
    assert "Rows loaded: 1" in result.stdout
    assert output.exists()
    assert report.exists()


def test_timeframe_duration_calibration_review_cli_fails_for_missing_input(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_timeframe_duration_calibration_review.py",
            "--experiment-summary",
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
    assert "H1/M5 duration calibration review failed: Duration experiment summary CSV not found" in result.stdout


def _row(scenario_id: str, timeframe: str, profile: str) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
        "Experiment_Profile": profile,
        "Status": "COMPLETED",
        "Max_Structure_Duration_Seconds": 14400,
        "Structures_Detected": 10,
        "Average_Structure_Duration": 3600,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 12,
        "Direction_Alignment_Rate": 0.55,
        "Low_Sample_Conditions_Research": 10,
        "Low_Sample_Conditions_Price_Outcome": 8,
    }
