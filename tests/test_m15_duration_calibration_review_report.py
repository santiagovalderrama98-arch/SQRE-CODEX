from pathlib import Path

import pandas as pd

from sqre.m15_duration_calibration_review.models import (
    M15DurationReviewFinding,
    M15DurationReviewResult,
    M15DurationReviewRow,
)
from sqre.m15_duration_calibration_review.reports import (
    write_m15_duration_review_report,
    write_m15_duration_review_summary_csv,
)


def test_summary_writer_outputs_required_columns(tmp_path):
    output = tmp_path / "review.csv"

    write_m15_duration_review_summary_csv(output, [_review_row()])

    frame = pd.read_csv(output)
    assert list(frame["Timeframe"]) == ["M15"]
    assert "Experiment_Profile" in frame.columns
    assert "Relative_Structure_Change_vs_Baseline" in frame.columns
    assert "Profile_Diagnostic" in frame.columns


def test_report_writer_outputs_required_sections_and_safe_language(tmp_path):
    report = tmp_path / "review.txt"
    result = M15DurationReviewResult(
        input_experiment_summary="experiment_summary.csv",
        rows_loaded=35,
        profiles_reviewed=5,
        output_path=tmp_path / "review.csv",
        report_path=report,
        rows=[_review_row()],
    )
    findings = [
        M15DurationReviewFinding(
            timeframe="M15",
            experiment_profile="m15_duration_8h_baseline",
            finding_type="DURATION_PROFILE",
            flag="NEAR_MAX",
            message="Baseline reference profile. Duration utilization is 0.8600.",
        )
    ]

    write_m15_duration_review_report(report, result, findings)

    text = report.read_text(encoding="utf-8")
    assert "SQRE M15 Duration Calibration Review" in text
    assert "Executive Diagnostic Summary" in text
    assert "Experiment Coverage" in text
    assert "M15 Duration Profile Overview" in text
    assert "Baseline Comparison Review" in text
    assert "M15 Diagnostic Review" in text
    assert "Do Not Change Yet" in text
    assert "No comparative ordering is produced." in text
    assert not _contains_forbidden_language(text)


def _review_row() -> M15DurationReviewRow:
    return M15DurationReviewRow(
        timeframe="M15",
        experiment_profile="m15_duration_8h_baseline",
        scenario_count=7,
        completed_run_count=7,
        failed_run_count=0,
        missing_input_count=0,
        scenario_ids="eurusd_m15_period_1",
        max_structure_duration_seconds=28800,
        average_structures_detected=82,
        min_structures_detected=70,
        max_structures_detected=90,
        structure_count_range=20,
        structure_count_cv=0.12,
        average_structure_duration=25000,
        average_duration_utilization_ratio=0.86,
        min_duration_utilization_ratio=0.80,
        max_duration_utilization_ratio=0.90,
        average_unique_states=7,
        min_unique_states=6,
        max_unique_states=8,
        state_diversity_range=2,
        most_common_state_mode="DIRECTIONAL_DRIFT",
        directional_displacement_total=10,
        directional_expansion_total=8,
        directional_drift_total=6,
        volatile_rotation_total=4,
        complex_consolidation_total=3,
        low_quality_structure_total=2,
        unclassified_total=1,
        average_directional_state_ratio=0.4,
        average_complex_consolidation_ratio=0.2,
        average_volatile_rotation_ratio=0.1,
        average_low_quality_rate=0.05,
        average_unclassified_rate=0.01,
        average_forward_range_pips=8,
        average_outcome_magnitude_pips=4,
        average_direction_alignment_rate=0.4,
        average_low_sample_conditions_research=55,
        average_low_sample_conditions_price_outcome=20,
        max_low_sample_conditions_research=60,
        max_low_sample_conditions_price_outcome=30,
        baseline_profile="m15_duration_8h_baseline",
        baseline_structures_detected=82,
        relative_structure_change_vs_baseline=0.0,
        relative_duration_utilization_change_vs_baseline=0.0,
        relative_unique_states_change_vs_baseline=0.0,
        relative_low_sample_research_change_vs_baseline=0.0,
        relative_low_sample_price_outcome_change_vs_baseline=0.0,
        relative_forward_range_change_vs_baseline=0.0,
        relative_direction_alignment_change_vs_baseline=0.0,
        structure_stability_flag="STABLE",
        duration_utilization_flag="NEAR_MAX",
        state_diversity_flag="HIGH_DIVERSITY",
        low_sample_pressure_flag="HIGH",
        fragmentation_flag="BASELINE_REFERENCE",
        compression_flag="BASELINE_REFERENCE",
        profile_diagnostic="Baseline reference profile",
        recommended_follow_up="Use as reference only; do not change production defaults.",
    )


def _contains_forbidden_language(text: str) -> bool:
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
        "best profile",
        "ranking",
        "should trade",
        "predicts",
        "optimal",
    ]
    lower = text.lower()
    return any(term in lower for term in forbidden)
