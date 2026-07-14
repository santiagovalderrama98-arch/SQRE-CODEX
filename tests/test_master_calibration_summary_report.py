from pathlib import Path

import pandas as pd

from sqre.master_calibration_summary.models import DuplicateScenarioDetail, MasterCalibrationSummaryResult
from sqre.master_calibration_summary.reports import write_master_summary_report


def test_report_includes_accounting_and_timeframe_coverage(tmp_path: Path):
    output = tmp_path / "master.csv"
    report = tmp_path / "report.txt"
    pd.DataFrame(
        [
            {"Scenario_ID": "eurusd_m5_period_1", "Timeframe": "M5"},
            {"Scenario_ID": "eurusd_h1_period_1", "Timeframe": "H1"},
        ]
    ).to_csv(output, index=False)
    result = MasterCalibrationSummaryResult(
        requested_files=["first.csv", "missing.csv"],
        found_files=["first.csv"],
        missing_files=["missing.csv"],
        rows_loaded=3,
        rows_retained=2,
        duplicate_scenario_ids=["eurusd_m5_period_1"],
        duplicate_details=[
            DuplicateScenarioDetail(
                scenario_id="eurusd_m5_period_1",
                duplicate_count=2,
                retained_source_file="first.csv",
                retained_source_row_index=0,
                source_files=["old.csv", "first.csv"],
            )
        ],
        timeframe_counts={"M5": 1, "H1": 1},
        output_path=output,
        report_path=report,
        dedupe_policy="last",
    )

    write_master_summary_report(report, result)

    text = report.read_text()
    assert "Rows Loaded" in text
    assert "3" in text
    assert "Rows Retained" in text
    assert "2" in text
    assert "eurusd_m5_period_1" in text
    assert "- H1: 1" in text
    assert "- M5: 1" in text
    assert "retained_source=first.csv" in text


def test_report_excludes_forbidden_operational_language(tmp_path: Path):
    output = tmp_path / "master.csv"
    report = tmp_path / "report.txt"
    pd.DataFrame([{"Scenario_ID": "one", "Timeframe": "M5"}]).to_csv(output, index=False)
    result = MasterCalibrationSummaryResult(
        requested_files=["first.csv"],
        found_files=["first.csv"],
        missing_files=[],
        rows_loaded=1,
        rows_retained=1,
        duplicate_scenario_ids=[],
        duplicate_details=[],
        timeframe_counts={"M5": 1},
        output_path=output,
        report_path=report,
    )

    write_master_summary_report(report, result)

    text = report.read_text().lower()
    forbidden = [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "take profit",
        "stop loss",
        "profitable",
        "opportunity",
        "edge",
        "best timeframe",
        "ranking",
    ]
    assert not [word for word in forbidden if word in text]
