from __future__ import annotations

import pytest

from sqre.m15_duration_calibration_review.config import M15DurationCalibrationReviewConfig
from sqre.m15_duration_calibration_review.metrics import build_m15_duration_review_rows
from sqre.m15_duration_calibration_review.models import M15DurationExperimentRunRow


def test_metrics_group_by_timeframe_and_profile():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", structures=10),
            _run("two", "m15_duration_8h_baseline", structures=14),
            _run("one", "m15_duration_4h", structures=20, max_duration=14400),
        ],
        M15DurationCalibrationReviewConfig(),
    )

    by_profile = {row.experiment_profile: row for row in rows}
    assert by_profile["m15_duration_8h_baseline"].scenario_count == 2
    assert by_profile["m15_duration_8h_baseline"].average_structures_detected == 12
    assert by_profile["m15_duration_4h"].scenario_count == 1


def test_duration_utilization_ratio_is_computed_correctly():
    rows = build_m15_duration_review_rows(
        [_run("one", "m15_duration_8h_baseline", duration=14400, max_duration=28800)],
        M15DurationCalibrationReviewConfig(),
    )

    assert rows[0].average_duration_utilization_ratio == 0.5


def test_cv_calculations_handle_zero_mean():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", structures=0),
            _run("two", "m15_duration_8h_baseline", structures=0),
        ],
        M15DurationCalibrationReviewConfig(),
    )

    assert rows[0].structure_count_cv == 0.0


def test_baseline_comparison_works_against_m15_baseline():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", structures=20, duration=24000, max_duration=28800, low_sample=50),
            _run("one", "m15_duration_4h", structures=30, duration=12000, max_duration=14400, low_sample=60),
            _run("one", "m15_duration_12h", structures=10, duration=26000, max_duration=43200, low_sample=40),
        ],
        M15DurationCalibrationReviewConfig(),
    )
    by_profile = {row.experiment_profile: row for row in rows}

    assert by_profile["m15_duration_4h"].relative_structure_change_vs_baseline == 0.5
    assert by_profile["m15_duration_4h"].fragmentation_flag == "INCREASED_FRAGMENTATION"
    assert by_profile["m15_duration_12h"].relative_structure_change_vs_baseline == -0.5
    assert by_profile["m15_duration_12h"].compression_flag == "INCREASED_COMPRESSION"
    assert by_profile["m15_duration_8h_baseline"].profile_diagnostic == "Baseline reference profile"


def test_zero_baseline_relative_comparison_is_safe():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", structures=0),
            _run("one", "m15_duration_10h", structures=4, max_duration=36000),
        ],
        M15DurationCalibrationReviewConfig(),
    )
    candidate = next(row for row in rows if row.experiment_profile == "m15_duration_10h")

    assert candidate.relative_structure_change_vs_baseline is None


def test_ratio_fallback_works_without_fabricating_count_totals():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", has_state_counts=False, directional_ratio=0.6),
            _run("two", "m15_duration_8h_baseline", has_state_counts=False, directional_ratio=0.4),
        ],
        M15DurationCalibrationReviewConfig(),
    )

    row = rows[0]
    assert row.directional_displacement_total == 0
    assert row.directional_expansion_total == 0
    assert row.directional_drift_total == 0
    assert row.average_directional_state_ratio == pytest.approx(0.5)


def test_flags_are_assigned_correctly():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", structures=10, duration=26000, max_duration=28800, unique_states=8),
            _run("two", "m15_duration_8h_baseline", structures=30, duration=26000, max_duration=28800, unique_states=8),
        ],
        M15DurationCalibrationReviewConfig(high_structure_cv_threshold=0.10),
    )

    row = rows[0]
    assert row.structure_stability_flag == "VARIABLE"
    assert row.duration_utilization_flag == "NEAR_MAX"
    assert row.state_diversity_flag == "HIGH_DIVERSITY"


def test_diagnostics_and_follow_ups_are_descriptive():
    rows = build_m15_duration_review_rows(
        [
            _run("one", "m15_duration_8h_baseline", structures=20, max_duration=28800, low_sample=50),
            _run("one", "m15_duration_4h", structures=30, max_duration=14400, low_sample=60),
        ],
        M15DurationCalibrationReviewConfig(),
    )
    candidate = next(row for row in rows if row.experiment_profile == "m15_duration_4h")

    assert candidate.profile_diagnostic == "M15 shorter-duration profile increases structural fragmentation"
    assert candidate.recommended_follow_up == "Do not promote; retain for diagnostic comparison only."
    assert not _contains_forbidden_language(candidate.profile_diagnostic)
    assert not _contains_forbidden_language(candidate.recommended_follow_up)


def _run(
    scenario_id: str,
    profile: str,
    *,
    structures: int = 10,
    duration: float = 3600,
    max_duration: int = 28800,
    unique_states: int = 5,
    low_sample: int = 10,
    has_state_counts: bool = True,
    directional_ratio: float | None = None,
) -> M15DurationExperimentRunRow:
    return M15DurationExperimentRunRow(
        scenario_id=scenario_id,
        timeframe="M15",
        experiment_profile=profile,
        status="COMPLETED",
        max_structure_duration_seconds=max_duration,
        structures_detected=structures,
        average_structure_duration=duration,
        unique_states=unique_states,
        most_common_state="DIRECTIONAL_DISPLACEMENT",
        average_forward_range_pips=12,
        direction_alignment_rate=0.55,
        low_sample_conditions_research=low_sample,
        low_sample_conditions_price_outcome=8,
        states_generated=structures,
        directional_displacement_count=3 if has_state_counts else 0,
        directional_expansion_count=2 if has_state_counts else 0,
        directional_drift_count=1 if has_state_counts else 0,
        volatile_rotation_count=1 if has_state_counts else 0,
        complex_consolidation_count=2 if has_state_counts else 0,
        low_quality_structure_count=1 if has_state_counts else 0,
        unclassified_count=0,
        average_outcome_magnitude_pips=6,
        directional_state_ratio=directional_ratio,
        has_directional_count_columns=has_state_counts,
        has_complex_consolidation_count_column=has_state_counts,
        has_volatile_rotation_count_column=has_state_counts,
        has_low_quality_count_column=has_state_counts,
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
