from pathlib import Path

import pandas as pd
import pytest

from sqre.master_calibration_summary.loader import load_summary_csv, load_summary_csvs


def test_loader_reads_one_csv(tmp_path: Path):
    csv_path = tmp_path / "summary.csv"
    pd.DataFrame([_row("one", "M5")]).to_csv(csv_path, index=False)

    frame = load_summary_csv(csv_path)

    assert len(frame) == 1
    assert frame.loc[0, "Scenario_ID"] == "one"
    assert frame.loc[0, "Source_File"] == str(csv_path)
    assert frame.loc[0, "Source_Row_Index"] == 0


def test_loader_reads_multiple_csvs(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    pd.DataFrame([_row("one", "M5")]).to_csv(first, index=False)
    pd.DataFrame([_row("two", "H1")]).to_csv(second, index=False)

    loaded = load_summary_csvs([first, second])

    assert loaded.rows_loaded == 2
    assert loaded.found_files == [str(first), str(second)]
    assert loaded.missing_files == []
    assert loaded.frame["Scenario_ID"].tolist() == ["one", "two"]


def test_loader_handles_case_insensitive_required_columns(tmp_path: Path):
    csv_path = tmp_path / "summary.csv"
    row = {key.lower(): value for key, value in _row("one", "H4").items()}
    pd.DataFrame([row]).to_csv(csv_path, index=False)

    frame = load_summary_csv(csv_path)

    assert "Scenario_ID" in frame.columns
    assert "Timeframe" in frame.columns
    assert frame.loc[0, "Scenario_ID"] == "one"
    assert frame.loc[0, "Timeframe"] == "H4"


def test_loader_fails_clearly_when_required_columns_are_missing(tmp_path: Path):
    csv_path = tmp_path / "summary.csv"
    row = _row("one", "M5")
    row.pop("Scenario_ID")
    pd.DataFrame([row]).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        load_summary_csv(csv_path)


def test_missing_input_fails_when_not_allowed(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Validation summary CSV not found"):
        load_summary_csvs([tmp_path / "missing.csv"], allow_missing_inputs=False)


def test_missing_input_is_reported_when_allowed(tmp_path: Path):
    missing = tmp_path / "missing.csv"

    loaded = load_summary_csvs([missing], allow_missing_inputs=True)

    assert loaded.rows_loaded == 0
    assert loaded.found_files == []
    assert loaded.missing_files == [str(missing)]


def _row(scenario_id: str, timeframe: str) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Status": "COMPLETED",
        "Symbol": "EURUSD",
        "Timeframe": timeframe,
        "OHLC_File": f"data/raw/{scenario_id}.csv",
        "Period_Start": "2026-01-01",
        "Period_End": "2026-01-31",
        "OHLC_Rows": 100,
        "Structures_Detected": 10,
        "Average_Structure_Duration": 3600,
        "Unique_States": 5,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 12.5,
        "Direction_Alignment_Rate": 0.55,
    }
