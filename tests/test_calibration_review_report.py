from pathlib import Path

import pandas as pd

from sqre.calibration_review.models import CalibrationFinding, CalibrationMetricsRow, CalibrationReviewSummary
from sqre.calibration_review.reports import (
    SUMMARY_COLUMNS,
    write_calibration_review_report,
    write_calibration_review_summary_csv,
)


def _row() -> CalibrationMetricsRow:
    return CalibrationMetricsRow(
        scenario_id="eurusd_h1_period_1",
        symbol="EURUSD",
        timeframe="H1",
        status="COMPLETED",
        period_start="2026-01-01",
        period_end="2026-01-31",
        ohlc_rows=500,
        duration_utilization_ratio=0.5,
        most_common_state_ratio=0.4,
        directional_state_ratio=0.6,
        compression_consolidation_ratio=0.2,
        volatile_rotation_ratio=0.1,
        unclassified_rate=0.0,
        low_quality_rate=0.0,
        state_diversity=5,
        transition_diversity=4,
        state_change_rate=0.3,
        direction_change_rate=0.2,
        transition_stability=0.7,
        research_low_sample_rate=0.4,
        price_outcome_low_sample_rate=0.3,
        average_forward_range_pips=12.0,
        average_outcome_magnitude_pips=8.0,
        direction_alignment_rate=0.55,
        average_forward_close_return_pips=1.1,
        duration_near_max_flag=False,
        high_state_dominance_flag=False,
        low_state_diversity_flag=False,
        high_directional_ratio_flag=False,
        high_research_low_sample_flag=False,
        high_price_outcome_low_sample_flag=False,
        calibration_status="OK",
        calibration_notes="No diagnostic flags triggered.",
    )


def test_write_calibration_review_summary_csv_uses_expected_columns(tmp_path: Path):
    output = tmp_path / "calibration_review_summary.csv"

    write_calibration_review_summary_csv(output, [_row()])

    frame = pd.read_csv(output)
    assert list(frame.columns) == SUMMARY_COLUMNS
    assert frame.loc[0, "Scenario_ID"] == "eurusd_h1_period_1"


def test_write_calibration_review_report_includes_required_sections(tmp_path: Path):
    report = tmp_path / "calibration_review_report.txt"
    summary = CalibrationReviewSummary(
        input_files=["summary.csv"],
        scenarios_loaded=1,
        completed_scenarios=1,
        summary_rows=1,
        finding_count=1,
        review_status="WATCH",
        output_path=tmp_path / "summary_out.csv",
        report_path=report,
    )
    finding = CalibrationFinding(
        finding_id="CAL_000001",
        finding_type="TEMPORAL_CONSISTENCY",
        severity="INFO",
        scope="TIMEFRAME",
        timeframe="H1",
        scenario_id="a|b",
        metric_name="temporal_consistency",
        metric_value=1.0,
        threshold=1.0,
        message="Temporal metrics are broadly consistent across periods for this timeframe.",
    )

    write_calibration_review_report(report, summary, [_row()], [finding])

    text = report.read_text(encoding="utf-8")
    assert "SQRE Calibration Review Report" in text
    assert "Market Structure Calibration Review" in text
    assert "Market States Calibration Review" in text
    assert "Transition Calibration Review" in text
    assert "Price Outcome Calibration Review" in text
    assert "Temporal Consistency Review" in text
    assert "Potential Calibration Issues" in text
    assert "Candidate Adjustments for Phase 7.4.1" in text
    assert "Do Not Change Yet" in text
    assert "No thresholds were modified." in text


def test_calibration_review_report_avoids_operational_language(tmp_path: Path):
    report = tmp_path / "calibration_review_report.txt"
    summary = CalibrationReviewSummary(scenarios_loaded=1, summary_rows=1, report_path=report)

    write_calibration_review_report(report, summary, [_row()], [])

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
    ]
    assert not [term for term in forbidden if term in text]
