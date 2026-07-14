from pathlib import Path

import pandas as pd

from sqre.timeframe_duration_calibration_review import run_timeframe_duration_calibration_review


def test_pipeline_writes_review_summary_csv_and_report(tmp_path: Path):
    summary = tmp_path / "experiment_summary.csv"
    output = tmp_path / "review_summary.csv"
    report = tmp_path / "review_report.txt"
    pd.DataFrame(
        [
            _row("one", "H1", "h1_duration_24h_baseline", 10),
            _row("one", "H1", "h1_duration_18h", 14),
        ]
    ).to_csv(summary, index=False)

    result = run_timeframe_duration_calibration_review(summary, output, report)

    frame = pd.read_csv(output)
    assert result.rows_loaded == 2
    assert result.timeframes_reviewed == 1
    assert result.profiles_reviewed == 2
    assert output.exists()
    assert report.exists()
    assert set(frame["Experiment_Profile"]) == {"h1_duration_24h_baseline", "h1_duration_18h"}


def _row(scenario_id: str, timeframe: str, profile: str, structures: int) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
        "Experiment_Profile": profile,
        "Status": "COMPLETED",
        "Max_Structure_Duration_Seconds": 86400,
        "Structures_Detected": structures,
        "Average_Structure_Duration": 3600,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 12,
        "Direction_Alignment_Rate": 0.55,
        "Low_Sample_Conditions_Research": 10,
        "Low_Sample_Conditions_Price_Outcome": 8,
    }
