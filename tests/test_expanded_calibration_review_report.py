from pathlib import Path

from sqre.expanded_calibration_review.findings import generate_expanded_calibration_findings
from sqre.expanded_calibration_review.models import ExpandedCalibrationReviewSummary, TimeframeCalibrationReviewRow
from sqre.expanded_calibration_review.reports import (
    SUMMARY_COLUMNS,
    write_expanded_calibration_review_report,
    write_expanded_calibration_review_summary_csv,
)


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path: Path):
    row = _row()
    report = tmp_path / "report.txt"
    write_expanded_calibration_review_report(
        report,
        ExpandedCalibrationReviewSummary(input_files=["input.csv"], rows_loaded=2, timeframes_reviewed=1, summary_rows=1),
        [row],
        generate_expanded_calibration_findings([row], config=_config()),
    )

    text = report.read_text(encoding="utf-8")
    required_sections = [
        "SQRE Expanded Historical Calibration Review",
        "Executive Diagnostic Summary",
        "Timeframe Overview",
        "Structural Stability Review",
        "State Diversity Review",
        "Low Sample Pressure Review",
        "Price Outcome Regime Sensitivity Review",
        "Diagnostic Findings",
        "Potential Follow-Up Areas",
        "Do Not Change Yet",
        "Limitations",
    ]
    forbidden = [
        "Buy",
        "Sell",
        "Entry",
        "Exit",
        "Trade signal",
        "Trade setup",
        "Take profit",
        "Stop loss",
        "Profitable",
        "Opportunity",
        "Recommendation to trade",
        "Edge",
        "Best timeframe",
        "Best profile",
        "Should trade",
        "Predicts",
    ]
    assert all(section in text for section in required_sections)
    assert not any(term in text for term in forbidden)


def test_summary_csv_contains_required_columns(tmp_path: Path):
    output = tmp_path / "summary.csv"

    write_expanded_calibration_review_summary_csv(output, [_row()])

    header = output.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert header == SUMMARY_COLUMNS


def _config():
    from sqre.expanded_calibration_review.config import ExpandedCalibrationReviewConfig

    return ExpandedCalibrationReviewConfig()


def _row() -> TimeframeCalibrationReviewRow:
    return TimeframeCalibrationReviewRow(
        timeframe="H4",
        scenario_count=2,
        scenario_ids="a;b",
        average_ohlc_rows=100,
        total_ohlc_rows=200,
        average_structures_detected=10,
        min_structures_detected=9,
        max_structures_detected=11,
        structure_count_range=2,
        structure_count_cv=0.1,
        average_structure_duration=1000,
        min_average_structure_duration=900,
        max_average_structure_duration=1100,
        structure_duration_cv=0.1,
        average_unique_states=5,
        min_unique_states=5,
        max_unique_states=5,
        state_diversity_range=0,
        most_common_state_mode="DIRECTIONAL_DISPLACEMENT",
        directional_displacement_total=6,
        directional_expansion_total=2,
        volatile_rotation_total=2,
        complex_consolidation_total=3,
        low_quality_structure_total=1,
        unclassified_total=1,
        average_directional_state_ratio=0.5,
        average_complex_consolidation_ratio=0.2,
        average_volatile_rotation_ratio=0.1,
        average_low_quality_rate=0.05,
        average_unclassified_rate=0.05,
        average_forward_range_pips=25,
        min_forward_range_pips=20,
        max_forward_range_pips=30,
        forward_range_cv=0.15,
        average_outcome_magnitude_pips=12,
        average_direction_alignment_rate=0.55,
        min_direction_alignment_rate=0.5,
        max_direction_alignment_rate=0.6,
        average_low_sample_conditions_research=5,
        average_low_sample_conditions_price_outcome=4,
        max_low_sample_conditions_research=6,
        max_low_sample_conditions_price_outcome=5,
        structural_stability_flag="STABLE",
        state_diversity_flag="BALANCED_DIVERSITY",
        low_sample_pressure_flag="MODERATE",
        forward_range_regime_sensitivity_flag="MODERATE",
        unclassified_pressure_flag="LOW",
        low_quality_pressure_flag="LOW",
        diagnostic_profile="Balanced structural research timeframe",
        recommended_follow_up="Maintain baseline structure settings and continue calibration monitoring.",
    )
