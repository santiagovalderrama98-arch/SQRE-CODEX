from pathlib import Path

import pandas as pd

from sqre.calibration_review.calibration_review_pipeline import run_calibration_review


def test_run_calibration_review_writes_summary_and_report(tmp_path: Path):
    summary_csv = tmp_path / "validation_summary.csv"
    output = tmp_path / "calibration_review_summary.csv"
    report = tmp_path / "calibration_review_report.txt"
    pd.DataFrame(
        [
            {
                "Scenario_ID": "eurusd_h1_period_1",
                "Status": "COMPLETED",
                "Symbol": "EURUSD",
                "Timeframe": "H1",
                "Period_Start": "2026-01-01",
                "Period_End": "2026-01-31",
                "OHLC_Rows": 500,
                "Max_Structure_Duration_Seconds": 14400,
                "Average_Structure_Duration": 7200,
                "States_Generated": 10,
                "Unique_States": 5,
                "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
                "Directional_Displacement_Count": 4,
                "Conditions_Evaluated": 20,
                "Low_Sample_Conditions_Research": 5,
                "Price_Outcome_Summary_Rows": 10,
                "Low_Sample_Conditions_Price_Outcome": 3,
            }
        ]
    ).to_csv(summary_csv, index=False)

    result = run_calibration_review([summary_csv], output, report)

    assert result.scenarios_loaded == 1
    assert result.summary_rows == 1
    assert output.exists()
    assert report.exists()
    assert pd.read_csv(output).loc[0, "Scenario_ID"] == "eurusd_h1_period_1"


def test_run_calibration_review_deduplicates_multiple_inputs(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "summary.csv"
    report = tmp_path / "report.txt"
    row = {
        "Scenario_ID": "same",
        "Status": "COMPLETED",
        "Symbol": "EURUSD",
        "Timeframe": "M5",
        "Period_Start": "2026-01-01",
        "Period_End": "2026-01-31",
    }
    pd.DataFrame([{**row, "OHLC_Rows": 10}]).to_csv(first, index=False)
    pd.DataFrame([{**row, "OHLC_Rows": 20}]).to_csv(second, index=False)

    result = run_calibration_review([first, second], output, report)

    frame = pd.read_csv(output)
    assert result.scenarios_loaded == 1
    assert frame.loc[0, "OHLC_Rows"] == 20
