from __future__ import annotations

import pytest

from sqre.m15_introduction_review.config import M15IntroductionReviewConfig
from sqre.m15_introduction_review.metrics import build_m15_review_rows
from sqre.m15_introduction_review.models import M15Context, M15ValidationSummaryRow


def test_metrics_build_one_m15_row_with_counts_and_flags():
    rows = [
        _row("eurusd_m15_period_1", 10, 7200, 4, "DIRECTIONAL_DRIFT", 8, 4, 0.4),
        _row("eurusd_m15_period_2", 14, 8200, 6, "VOLATILE_ROTATION", 12, 6, 0.5),
    ]

    review_rows = build_m15_review_rows(rows, M15IntroductionReviewConfig(), M15Context())

    row = review_rows[0]
    assert row.timeframe == "M15"
    assert row.scenario_count == 2
    assert row.completed_scenario_count == 2
    assert row.average_structures_detected == 12
    assert row.structure_count_range == 4
    assert row.average_duration_utilization_ratio == pytest.approx(((7200 + 8200) / 2) / 28800)
    assert row.structure_stability_flag == "STABLE"
    assert row.state_diversity_flag == "BALANCED_DIVERSITY"
    assert row.low_sample_pressure_flag == "MODERATE"


def test_metrics_uses_ratio_fallback_when_count_columns_are_missing():
    rows = [
        _row("eurusd_m15_period_1", 10, 7200, 4, "DIRECTIONAL_DRIFT", 8, 4, 0.4, ratio=0.30, has_counts=False),
        _row("eurusd_m15_period_2", 10, 7200, 4, "DIRECTIONAL_DRIFT", 8, 4, 0.4, ratio=0.50, has_counts=False),
    ]

    review_rows = build_m15_review_rows(rows, M15IntroductionReviewConfig(), M15Context())

    assert review_rows[0].directional_displacement_total == 0
    assert review_rows[0].average_directional_state_ratio == pytest.approx(0.40)


def test_metrics_filters_non_m15_rows_and_preserves_context():
    rows = [
        _row("eurusd_m15_period_1", 10, 7200, 4, "DIRECTIONAL_DRIFT", 8, 4, 0.4),
        _row("eurusd_h1_period_1", 100, 20000, 7, "DIRECTIONAL_EXPANSION", 8, 4, 0.4, timeframe="H1"),
    ]
    context = M15Context(m5_average_structures=8, h1_average_structures=20, interpretation="Context ready.")

    review_rows = build_m15_review_rows(rows, M15IntroductionReviewConfig(), context)

    assert review_rows[0].scenario_count == 1
    assert review_rows[0].m5_average_structures_context == 8
    assert review_rows[0].h1_average_structures_context == 20
    assert review_rows[0].context_interpretation == "Context ready."


def test_metrics_marks_missing_inputs_without_crashing():
    rows = [_row("eurusd_m15_period_1", 0, 0, 0, "", 0, 0, 0, status="MISSING_INPUT")]

    review_rows = build_m15_review_rows(rows, M15IntroductionReviewConfig(), M15Context())

    row = review_rows[0]
    assert row.missing_input_count == 1
    assert row.completed_scenario_count == 0
    assert row.m15_diagnostic_profile == "M15 requires further diagnostic review"


def test_metrics_flags_near_max_duration_before_candidate():
    rows = [_row("eurusd_m15_period_1", 10, 26000, 5, "DIRECTIONAL_DRIFT", 8, 4, 0.4)]

    review_rows = build_m15_review_rows(rows, M15IntroductionReviewConfig(), M15Context())

    assert review_rows[0].duration_utilization_flag == "NEAR_MAX"
    assert review_rows[0].m15_diagnostic_profile == "Intraday timeframe requiring duration review"


def _row(
    scenario_id: str,
    structures: int,
    duration: float,
    unique_states: int,
    state: str,
    forward_range: float,
    low_sample: int,
    alignment: float,
    *,
    timeframe: str = "M15",
    status: str = "COMPLETED",
    ratio: float | None = None,
    has_counts: bool = True,
) -> M15ValidationSummaryRow:
    return M15ValidationSummaryRow(
        scenario_id=scenario_id,
        timeframe=timeframe,
        status=status,
        ohlc_rows=100,
        structures_detected=structures,
        average_structure_duration=duration,
        unique_states=unique_states,
        most_common_state=state,
        average_forward_range_pips=forward_range,
        direction_alignment_rate=alignment,
        low_sample_conditions_research=low_sample,
        low_sample_conditions_price_outcome=low_sample,
        states_generated=structures,
        directional_displacement_count=structures if has_counts else 0,
        directional_state_ratio=ratio,
        has_directional_count_columns=has_counts,
    )
