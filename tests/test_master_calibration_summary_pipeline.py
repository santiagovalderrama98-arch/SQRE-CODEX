from pathlib import Path

import pandas as pd

from sqre.master_calibration_summary import MasterCalibrationSummaryConfig, build_master_calibration_summary


def test_pipeline_writes_master_summary_csv_and_report(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "master.csv"
    report = tmp_path / "report.txt"
    pd.DataFrame([_row("eurusd_m5_period_1", "M5", 10), _row("eurusd_h1_period_1", "H1", 20)]).to_csv(
        first, index=False
    )
    pd.DataFrame([_row("eurusd_m5_period_1", "M5", 30), _row("eurusd_h4_period_1", "H4", 40)]).to_csv(
        second, index=False
    )

    result = build_master_calibration_summary(
        [first, second],
        output,
        report,
        MasterCalibrationSummaryConfig(dedupe_policy="last"),
    )

    frame = pd.read_csv(output)
    assert result.rows_loaded == 4
    assert result.rows_retained == 3
    assert result.duplicate_scenario_ids == ["eurusd_m5_period_1"]
    assert frame.loc[frame["Scenario_ID"] == "eurusd_m5_period_1", "Structures_Detected"].iloc[0] == 30
    assert set(frame["Timeframe"]) == {"M5", "H1", "H4"}
    assert output.exists()
    assert report.exists()
    assert "Duplicate Scenario IDs" in report.read_text()


def _row(scenario_id: str, timeframe: str, structures: int) -> dict[str, object]:
    return {
        "Scenario_ID": scenario_id,
        "Status": "COMPLETED",
        "Symbol": "EURUSD",
        "Timeframe": timeframe,
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
        "Optional_Metric": 99,
    }
