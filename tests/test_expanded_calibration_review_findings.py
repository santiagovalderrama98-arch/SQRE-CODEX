from sqre.expanded_calibration_review.config import ExpandedCalibrationReviewConfig
from sqre.expanded_calibration_review.findings import generate_expanded_calibration_findings
from sqre.expanded_calibration_review.models import TimeframeCalibrationReviewRow


def test_findings_include_required_flags_and_scenario_coverage():
    row = _row()

    findings = generate_expanded_calibration_findings(
        [row],
        ExpandedCalibrationReviewConfig(min_scenarios_per_timeframe=2),
    )

    types = {finding.finding_type for finding in findings}
    assert "SCENARIO_COVERAGE" in types
    assert "STRUCTURAL_STABILITY" in types
    assert "STATE_DIVERSITY" in types
    assert "LOW_SAMPLE_PRESSURE" in types
    assert "FORWARD_RANGE_REGIME_SENSITIVITY" in types
    assert "UNCLASSIFIED_PRESSURE" in types
    assert "LOW_QUALITY_PRESSURE" in types


def test_profiles_and_followups_are_descriptive_and_non_ranking():
    row = _row()
    forbidden = ["best", "worst", "rank", "ranking", "profitable", "trade", "signal", "edge"]

    text = f"{row.diagnostic_profile} {row.recommended_follow_up}".lower()

    assert not any(term in text for term in forbidden)


def _row() -> TimeframeCalibrationReviewRow:
    return TimeframeCalibrationReviewRow(
        timeframe="H4",
        scenario_count=1,
        scenario_ids="h4_a",
        average_ohlc_rows=100,
        total_ohlc_rows=100,
        average_structures_detected=10,
        min_structures_detected=10,
        max_structures_detected=10,
        structure_count_range=0,
        structure_count_cv=0,
        average_structure_duration=10,
        min_average_structure_duration=10,
        max_average_structure_duration=10,
        structure_duration_cv=0,
        average_unique_states=5,
        min_unique_states=5,
        max_unique_states=5,
        state_diversity_range=0,
        most_common_state_mode="DIRECTIONAL_DISPLACEMENT",
        directional_displacement_total=4,
        directional_expansion_total=2,
        volatile_rotation_total=1,
        complex_consolidation_total=2,
        low_quality_structure_total=0,
        unclassified_total=0,
        average_directional_state_ratio=0.6,
        average_complex_consolidation_ratio=0.2,
        average_volatile_rotation_ratio=0.1,
        average_low_quality_rate=0.0,
        average_unclassified_rate=0.0,
        average_forward_range_pips=25,
        min_forward_range_pips=20,
        max_forward_range_pips=30,
        forward_range_cv=0.1,
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
