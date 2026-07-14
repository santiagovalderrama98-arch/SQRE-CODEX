from __future__ import annotations

from sqre.timeframe_duration_calibration_review.config import TimeframeDurationCalibrationReviewConfig
from sqre.timeframe_duration_calibration_review.metrics import build_duration_review_rows
from sqre.timeframe_duration_calibration_review.models import DurationExperimentRunRow


def test_metrics_group_by_timeframe_and_profile():
    rows = build_duration_review_rows(
        [
            _run("one", "H1", "h1_duration_24h_baseline", structures=10),
            _run("two", "H1", "h1_duration_24h_baseline", structures=14),
            _run("three", "M5", "m5_duration_4h_baseline", structures=20),
        ],
        TimeframeDurationCalibrationReviewConfig(),
    )

    by_key = {(row.timeframe, row.experiment_profile): row for row in rows}
    assert by_key[("H1", "h1_duration_24h_baseline")].scenario_count == 2
    assert by_key[("H1", "h1_duration_24h_baseline")].average_structures_detected == 12
    assert by_key[("M5", "m5_duration_4h_baseline")].scenario_count == 1


def test_duration_utilization_ratio_is_computed_correctly():
    rows = build_duration_review_rows(
        [_run("one", "H1", "h1_duration_24h_baseline", duration=43200, max_duration=86400)],
        TimeframeDurationCalibrationReviewConfig(),
    )

    assert rows[0].average_duration_utilization_ratio == 0.5


def test_cv_calculations_handle_zero_mean():
    rows = build_duration_review_rows(
        [
            _run("one", "H1", "h1_duration_24h_baseline", structures=0),
            _run("two", "H1", "h1_duration_24h_baseline", structures=0),
        ],
        TimeframeDurationCalibrationReviewConfig(),
    )

    assert rows[0].structure_count_cv == 0.0


def test_baseline_comparison_works_for_h1_and_m5():
    rows = build_duration_review_rows(
        [
            _run("h1_a", "H1", "h1_duration_24h_baseline", structures=10, low_sample_research=20),
            _run("h1_a", "H1", "h1_duration_18h", structures=15, low_sample_research=10),
            _run("m5_a", "M5", "m5_duration_4h_baseline", structures=20),
            _run("m5_a", "M5", "m5_duration_6h", structures=10),
        ],
        TimeframeDurationCalibrationReviewConfig(),
    )
    by_key = {(row.timeframe, row.experiment_profile): row for row in rows}

    assert by_key[("H1", "h1_duration_18h")].relative_structure_change_vs_baseline == 0.5
    assert by_key[("H1", "h1_duration_18h")].relative_low_sample_research_change_vs_baseline == -0.5
    assert by_key[("M5", "m5_duration_6h")].relative_structure_change_vs_baseline == -0.5
    assert by_key[("M5", "m5_duration_6h")].compression_flag == "INCREASED_COMPRESSION"


def test_zero_baseline_relative_comparison_is_safe():
    rows = build_duration_review_rows(
        [
            _run("h1_a", "H1", "h1_duration_24h_baseline", structures=0),
            _run("h1_a", "H1", "h1_duration_30h", structures=4),
        ],
        TimeframeDurationCalibrationReviewConfig(),
    )
    candidate = next(row for row in rows if row.experiment_profile == "h1_duration_30h")

    assert candidate.relative_structure_change_vs_baseline is None


def test_flags_are_assigned_correctly():
    rows = build_duration_review_rows(
        [
            _run("one", "M5", "m5_duration_4h_baseline", structures=10, duration=13000, max_duration=14400),
            _run("two", "M5", "m5_duration_4h_baseline", structures=30, duration=13000, max_duration=14400),
        ],
        TimeframeDurationCalibrationReviewConfig(high_structure_cv_threshold=0.10),
    )

    row = rows[0]
    assert row.structure_stability_flag == "VARIABLE"
    assert row.duration_utilization_flag == "NEAR_MAX"


def _run(
    scenario_id: str,
    timeframe: str,
    profile: str,
    *,
    structures: int = 10,
    duration: float = 3600,
    max_duration: int | None = None,
    low_sample_research: int = 10,
) -> DurationExperimentRunRow:
    max_seconds = max_duration or (86400 if timeframe == "H1" else 14400)
    return DurationExperimentRunRow(
        scenario_id=scenario_id,
        timeframe=timeframe,
        experiment_profile=profile,
        status="COMPLETED",
        max_structure_duration_seconds=max_seconds,
        structures_detected=structures,
        average_structure_duration=duration,
        unique_states=5,
        most_common_state="DIRECTIONAL_DISPLACEMENT",
        average_forward_range_pips=12,
        direction_alignment_rate=0.55,
        low_sample_conditions_research=low_sample_research,
        low_sample_conditions_price_outcome=8,
        states_generated=structures,
        directional_displacement_count=3,
        directional_expansion_count=2,
        directional_drift_count=1,
        volatile_rotation_count=1,
        complex_consolidation_count=2,
        low_quality_structure_count=1,
        unclassified_count=0,
        average_outcome_magnitude_pips=6,
    )
