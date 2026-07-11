from pathlib import Path

import pandas as pd

from sqre.expanded_calibration_review.expanded_calibration_review_pipeline import run_expanded_calibration_review


def test_pipeline_writes_summary_csv_and_report(tmp_path: Path):
    summary_csv = tmp_path / "expanded_summary.csv"
    output = tmp_path / "review_summary.csv"
    report = tmp_path / "review_report.txt"
    pd.DataFrame(
        [
            _row("eurusd_h4_period_1", "H4", 10),
            _row("eurusd_h4_period_2", "H4", 12),
            _row("eurusd_d1_period_1", "D1", 4, forward_range=50),
            _row("eurusd_d1_period_2", "D1", 4, forward_range=90),
        ]
    ).to_csv(summary_csv, index=False)

    result = run_expanded_calibration_review([summary_csv], output, report)

    frame = pd.read_csv(output)
    assert result.rows_loaded == 4
    assert result.timeframes_reviewed == 2
    assert output.exists()
    assert report.exists()
    assert set(frame["Timeframe"]) == {"D1", "H4"}
    assert "Diagnostic_Profile" in frame.columns


def _row(scenario_id: str, timeframe: str, structures: int, *, forward_range: float = 25.0) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
        "OHLC_Rows": 1000,
        "Structures_Detected": structures,
        "Average_Structure_Duration": 3600,
        "States_Generated": structures,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Directional_Displacement_Count": 4,
        "Directional_Expansion_Count": 2,
        "Volatile_Rotation_Count": 1,
        "Complex_Consolidation_Count": 2,
        "Low_Quality_Structure_Count": 0,
        "Unclassified_Count": 0,
        "Average_Forward_Range_Pips": forward_range,
        "Average_Outcome_Magnitude_Pips": 10,
        "Direction_Alignment_Rate": 0.55,
        "Low_Sample_Conditions_Research": 4,
        "Low_Sample_Conditions_Price_Outcome": 3,
    }
