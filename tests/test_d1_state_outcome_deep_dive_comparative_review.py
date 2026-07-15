from sqre.d1_state_outcome_deep_dive.comparative_review import build_regime_comparison_matrix
from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.models import OutcomeStatisticsRow, RegimeBreakdownRow


def test_comparative_review_computes_regime_deviation_class():
    rows = build_regime_comparison_matrix(
        [_breakdown(range_pips=40, magnitude=20, alignment=0.2)],
        [_stats(range_pips=20, magnitude=10, alignment=0.6)],
        D1StateOutcomeDeepDiveConfig(high_dispersion_threshold=0.35, moderate_dispersion_threshold=0.2),
    )

    assert rows[0].forward_range_vs_profile_avg == 20
    assert rows[0].outcome_magnitude_vs_profile_avg == 10
    assert rows[0].regime_deviation_class == "HIGH_DEVIATION"


def test_comparative_review_handles_zero_profile_average_safely():
    rows = build_regime_comparison_matrix(
        [_breakdown(range_pips=0, magnitude=0, alignment=0)],
        [_stats(range_pips=0, magnitude=0, alignment=0)],
        D1StateOutcomeDeepDiveConfig(),
    )

    assert rows[0].regime_deviation_class == "LOW_DEVIATION"


def _breakdown(range_pips: float, magnitude: float, alignment: float) -> RegimeBreakdownRow:
    return RegimeBreakdownRow(
        condition_label="DIRECTIONAL_EXPANSION",
        forward_window=3,
        profile_type="RESEARCH_READY",
        regime_id="R1",
        regime_label="Regime 1",
        scenario_id="S1",
        sample_size=20,
        average_forward_close_return_pips=2,
        median_forward_close_return_pips=2,
        average_forward_range_pips=range_pips,
        average_favorable_displacement_pips=range_pips,
        average_adverse_displacement_pips=0,
        average_outcome_magnitude_pips=magnitude,
        direction_alignment_rate=alignment,
        sample_adequacy_flag="ADEQUATE",
        regime_observation_diagnostic="ok",
    )


def _stats(range_pips: float, magnitude: float, alignment: float) -> OutcomeStatisticsRow:
    return OutcomeStatisticsRow(
        condition_label="DIRECTIONAL_EXPANSION",
        forward_window=3,
        profile_type="RESEARCH_READY",
        regime_count=1,
        total_sample_size=20,
        average_sample_size_per_regime=20,
        average_forward_close_return_pips=1,
        min_forward_close_return_pips=1,
        max_forward_close_return_pips=1,
        forward_close_return_dispersion_pips=0,
        average_forward_range_pips=range_pips,
        min_forward_range_pips=range_pips,
        max_forward_range_pips=range_pips,
        forward_range_dispersion_pips=0,
        forward_range_cv=0,
        average_outcome_magnitude_pips=magnitude,
        min_outcome_magnitude_pips=magnitude,
        max_outcome_magnitude_pips=magnitude,
        outcome_magnitude_dispersion_pips=0,
        outcome_magnitude_cv=0,
        average_direction_alignment_rate=alignment,
        min_direction_alignment_rate=alignment,
        max_direction_alignment_rate=alignment,
        direction_alignment_dispersion=0,
        outcome_profile_stability_class="STABLE_DESCRIPTIVE",
        outcome_profile_diagnostic="ok",
        recommended_follow_up="ok",
    )
