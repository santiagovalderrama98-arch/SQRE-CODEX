from pathlib import Path

import pandas as pd

from sqre.expanded_calibration_review.loader import load_expanded_summaries, load_expanded_summary_csv


def test_loader_reads_one_csv(tmp_path: Path):
    path = tmp_path / "summary.csv"
    pd.DataFrame([_row("eurusd_h4_period_1", "H4")]).to_csv(path, index=False)

    rows = load_expanded_summary_csv(path)

    assert len(rows) == 1
    assert rows[0].scenario_id == "eurusd_h4_period_1"
    assert rows[0].timeframe == "H4"
    assert rows[0].structures_detected == 12


def test_loader_reads_multiple_csvs(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    pd.DataFrame([_row("one", "M5")]).to_csv(first, index=False)
    pd.DataFrame([_row("two", "D1")]).to_csv(second, index=False)

    rows = load_expanded_summaries([first, second])

    assert [row.scenario_id for row in rows] == ["one", "two"]


def test_loader_handles_case_insensitive_columns_and_missing_optional_counts(tmp_path: Path):
    path = tmp_path / "summary.csv"
    pd.DataFrame(
        [
            {
                "scenario_id": "lowercase",
                "timeframe": "H1",
                "ohlc_rows": 100,
                "structures_detected": 7,
                "average_structure_duration": 10.5,
            }
        ]
    ).to_csv(path, index=False)

    row = load_expanded_summary_csv(path)[0]

    assert row.scenario_id == "lowercase"
    assert row.timeframe == "H1"
    assert row.ohlc_rows == 100
    assert row.directional_displacement_count == 0
    assert row.low_sample_conditions_research == 0


def _row(scenario_id: str, timeframe: str) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Timeframe": timeframe,
        "OHLC_Rows": 1000,
        "Structures_Detected": 12,
        "Average_Structure_Duration": 3600,
        "States_Generated": 12,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Directional_Displacement_Count": 4,
        "Directional_Expansion_Count": 2,
        "Volatile_Rotation_Count": 1,
        "Complex_Consolidation_Count": 3,
        "Low_Quality_Structure_Count": 1,
        "Unclassified_Count": 1,
        "Average_Forward_Range_Pips": 25.0,
        "Average_Outcome_Magnitude_Pips": 10.0,
        "Direction_Alignment_Rate": 0.55,
        "Low_Sample_Conditions_Research": 5,
        "Low_Sample_Conditions_Price_Outcome": 4,
    }
