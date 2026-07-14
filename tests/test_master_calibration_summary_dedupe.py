import pandas as pd
import pytest

from sqre.master_calibration_summary.dedupe import dedupe_summary_frame


def test_dedupe_policy_first_keeps_first_duplicate():
    frame = pd.DataFrame([_row("dup", "first.csv", 0, 10), _row("dup", "second.csv", 0, 20)])

    result = dedupe_summary_frame(frame, dedupe_policy="first")

    assert result.rows_loaded == 2
    assert result.rows_retained == 1
    assert result.frame.loc[0, "Source_File"] == "first.csv"
    assert result.frame.loc[0, "Duplicate_Count_For_Scenario"] == 2
    assert bool(result.frame.loc[0, "Was_Duplicate"]) is True
    assert result.frame.loc[0, "Dedupe_Policy"] == "first"


def test_dedupe_policy_last_keeps_last_duplicate():
    frame = pd.DataFrame([_row("dup", "first.csv", 0, 10), _row("dup", "second.csv", 0, 20)])

    result = dedupe_summary_frame(frame, dedupe_policy="last")

    assert result.frame.loc[0, "Source_File"] == "second.csv"
    assert result.duplicate_scenario_ids == ["dup"]
    assert result.duplicate_details[0].retained_source_file == "second.csv"


def test_dedupe_policy_error_fails_on_duplicate():
    frame = pd.DataFrame([_row("dup", "first.csv", 0, 10), _row("dup", "second.csv", 0, 20)])

    with pytest.raises(ValueError, match="Duplicate Scenario_ID values found"):
        dedupe_summary_frame(frame, dedupe_policy="error")


def test_dedupe_adds_duplicate_metadata_for_unique_rows():
    frame = pd.DataFrame([_row("one", "first.csv", 0, 10), _row("two", "second.csv", 0, 20)])

    result = dedupe_summary_frame(frame)

    assert result.frame["Duplicate_Count_For_Scenario"].tolist() == [1, 1]
    assert result.frame["Was_Duplicate"].tolist() == [False, False]
    assert result.frame["Dedupe_Policy"].tolist() == ["last", "last"]


def _row(scenario_id: str, source_file: str, source_row_index: int, structures: int) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Status": "COMPLETED",
        "Symbol": "EURUSD",
        "Timeframe": "M5",
        "OHLC_File": f"data/raw/{scenario_id}.csv",
        "Period_Start": "2026-01-01",
        "Period_End": "2026-01-31",
        "OHLC_Rows": 100,
        "Structures_Detected": structures,
        "Average_Structure_Duration": 3600,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 12.5,
        "Direction_Alignment_Rate": 0.55,
        "Source_File": source_file,
        "Source_Row_Index": source_row_index,
    }
