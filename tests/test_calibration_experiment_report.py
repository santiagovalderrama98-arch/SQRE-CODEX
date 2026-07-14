from pathlib import Path

import pandas as pd

from sqre.calibration_experiments.models import CalibrationExperimentSummary, ExperimentMetricsRow
from sqre.calibration_experiments.reports import (
    SUMMARY_COLUMNS,
    write_calibration_experiment_report,
    write_calibration_experiment_summary_csv,
)


def _row(timeframe: str = "H4") -> ExperimentMetricsRow:
    scenario_id = f"eurusd_{timeframe.lower()}_period_1"
    return ExperimentMetricsRow(
        experiment_run_id=f"duration_baseline__{scenario_id}",
        experiment_type="DURATION",
        experiment_id="duration_baseline",
        scenario_id=scenario_id,
        symbol="EURUSD",
        timeframe=timeframe,
        status="COMPLETED",
        message="Completed successfully",
        structures_detected=10,
        average_structure_duration=100.0,
        duration_utilization_ratio=0.5,
        states_generated=10,
        unique_states=5,
        directional_state_ratio=0.4,
        average_forward_range_pips=12.0,
        research_low_sample_rate=0.2,
        price_outcome_low_sample_rate=0.3,
    )


def test_write_calibration_experiment_summary_csv(tmp_path: Path):
    output = tmp_path / "summary.csv"

    write_calibration_experiment_summary_csv(output, [_row()])

    frame = pd.read_csv(output)
    assert list(frame.columns) == SUMMARY_COLUMNS
    assert frame.loc[0, "Experiment_Run_ID"] == "duration_baseline__eurusd_h4_period_1"


def test_write_calibration_experiment_report_includes_required_sections(tmp_path: Path):
    report = tmp_path / "report.txt"
    summary = CalibrationExperimentSummary(
        experiment_name="calibration_experiments_v1",
        runs_configured=1,
        runs_completed=1,
        runs_missing_input=0,
        runs_failed=0,
        summary_rows=1,
        output_path=tmp_path / "summary.csv",
        report_path=report,
    )

    write_calibration_experiment_report(report, summary, [_row()])

    text = report.read_text(encoding="utf-8")
    assert "SQRE Calibration Experiment Report" in text
    assert "Experiment Scope" in text
    assert "Duration Sensitivity Summary" in text
    assert "Sample Size Sensitivity Summary" in text
    assert "Key Observations" in text
    assert "Potential Follow-Up Areas" in text
    assert "Do Not Change Yet" in text
    assert "No production thresholds were modified." in text
    assert "No Market State thresholds were changed." in text


def test_calibration_experiment_report_uses_dynamic_timeframe_scope(tmp_path: Path):
    report = tmp_path / "report.txt"
    summary = CalibrationExperimentSummary(
        experiment_name="h1_m5_duration_calibration_experiments_v1",
        runs_configured=2,
        runs_completed=2,
        runs_missing_input=0,
        runs_failed=0,
        summary_rows=2,
        output_path=tmp_path / "summary.csv",
        report_path=report,
    )

    write_calibration_experiment_report(report, summary, [_row("H1"), _row("M5")])

    text = report.read_text(encoding="utf-8")
    assert "- H1 and M5 scenarios" in text
    assert "- H4 and D1 scenarios" not in text


def test_calibration_experiment_report_keeps_h4_d1_scope_when_present(tmp_path: Path):
    report = tmp_path / "report.txt"
    summary = CalibrationExperimentSummary(
        experiment_name="calibration_experiments_v1",
        runs_configured=2,
        runs_completed=2,
        runs_missing_input=0,
        runs_failed=0,
        summary_rows=2,
        output_path=tmp_path / "summary.csv",
        report_path=report,
    )

    write_calibration_experiment_report(report, summary, [_row("H4"), _row("D1")])

    text = report.read_text(encoding="utf-8")
    assert "- H4 and D1 scenarios" in text


def test_calibration_experiment_report_avoids_forbidden_language(tmp_path: Path):
    report = tmp_path / "report.txt"
    summary = CalibrationExperimentSummary(
        experiment_name="calibration_experiments_v1",
        runs_configured=1,
        runs_completed=1,
        runs_missing_input=0,
        runs_failed=0,
        summary_rows=1,
        output_path=tmp_path / "summary.csv",
        report_path=report,
    )

    write_calibration_experiment_report(report, summary, [_row()])

    text = report.read_text(encoding="utf-8").lower()
    forbidden = [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "trade setup",
        "take profit",
        "stop loss",
        "profitable",
        "opportunity",
        "recommendation to trade",
        "edge",
        "best timeframe",
        "best condition",
        "should trade",
        "predicts",
        "best",
    ]
    assert not [term for term in forbidden if term in text]
