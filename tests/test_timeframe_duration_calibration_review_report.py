from pathlib import Path

from sqre.timeframe_duration_calibration_review.config import TimeframeDurationCalibrationReviewConfig
from sqre.timeframe_duration_calibration_review.findings import build_duration_review_findings
from sqre.timeframe_duration_calibration_review.metrics import build_duration_review_rows
from sqre.timeframe_duration_calibration_review.models import DurationExperimentRunRow, DurationReviewResult
from sqre.timeframe_duration_calibration_review.reports import write_duration_review_report


def test_report_includes_required_sections(tmp_path: Path):
    rows = build_duration_review_rows([_run("one", "H1", "h1_duration_24h_baseline")], TimeframeDurationCalibrationReviewConfig())
    result = DurationReviewResult(
        input_experiment_summary="summary.csv",
        rows_loaded=1,
        timeframes_reviewed=1,
        profiles_reviewed=1,
        output_path=tmp_path / "out.csv",
        report_path=tmp_path / "report.txt",
        rows=rows,
    )

    write_duration_review_report(result.report_path, result, build_duration_review_findings(rows))

    text = result.report_path.read_text()
    assert "SQRE H1/M5 Duration Calibration Review" in text
    assert "Executive Diagnostic Summary" in text
    assert "Experiment Coverage" in text
    assert "Baseline Comparison Review" in text
    assert "H1 Diagnostic Review" in text
    assert "M5 Diagnostic Review" in text
    assert "No comparative ordering is produced." in text


def test_report_excludes_forbidden_operational_language(tmp_path: Path):
    rows = build_duration_review_rows([_run("one", "M5", "m5_duration_4h_baseline")], TimeframeDurationCalibrationReviewConfig())
    result = DurationReviewResult(
        input_experiment_summary="summary.csv",
        rows_loaded=1,
        timeframes_reviewed=1,
        profiles_reviewed=1,
        output_path=tmp_path / "out.csv",
        report_path=tmp_path / "report.txt",
        rows=rows,
    )

    write_duration_review_report(result.report_path, result, build_duration_review_findings(rows))

    text = result.report_path.read_text().lower()
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
        "edge",
        "best timeframe",
        "best profile",
        "ranking",
        "should trade",
        "predicts",
    ]
    assert not [word for word in forbidden if word in text]


def _run(scenario_id: str, timeframe: str, profile: str) -> DurationExperimentRunRow:
    return DurationExperimentRunRow(
        scenario_id=scenario_id,
        timeframe=timeframe,
        experiment_profile=profile,
        status="COMPLETED",
        max_structure_duration_seconds=86400 if timeframe == "H1" else 14400,
        structures_detected=10,
        average_structure_duration=3600,
        unique_states=5,
        most_common_state="DIRECTIONAL_DISPLACEMENT",
        average_forward_range_pips=12,
        direction_alignment_rate=0.55,
        low_sample_conditions_research=10,
        low_sample_conditions_price_outcome=8,
    )
