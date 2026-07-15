from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.models import RegimeBreakdownRow
from sqre.d1_state_outcome_deep_dive.outcome_statistics import build_outcome_statistics, coefficient_of_variation


def test_outcome_statistics_compute_average_min_max_and_dispersion():
    rows = build_outcome_statistics(
        [
            _breakdown("R1", close=1, range_pips=10, magnitude=4, alignment=0.5),
            _breakdown("R2", close=3, range_pips=20, magnitude=8, alignment=0.7),
        ],
        D1StateOutcomeDeepDiveConfig(),
    )

    assert len(rows) == 1
    row = rows[0]
    assert row.average_forward_close_return_pips == 2.0
    assert row.min_forward_range_pips == 10
    assert row.max_forward_range_pips == 20
    assert row.forward_range_dispersion_pips == 10
    assert round(row.forward_range_cv, 4) == 0.6667
    assert row.outcome_profile_stability_class == "HIGH_DISPERSION"


def test_coefficient_of_variation_is_safe_when_average_is_zero():
    assert coefficient_of_variation(5, 0) == 0.0


def _breakdown(regime_id: str, close: float, range_pips: float, magnitude: float, alignment: float) -> RegimeBreakdownRow:
    return RegimeBreakdownRow(
        condition_label="DIRECTIONAL_EXPANSION",
        forward_window=3,
        profile_type="RESEARCH_READY",
        regime_id=regime_id,
        regime_label=regime_id,
        scenario_id=regime_id,
        sample_size=20,
        average_forward_close_return_pips=close,
        median_forward_close_return_pips=close,
        average_forward_range_pips=range_pips,
        average_favorable_displacement_pips=range_pips,
        average_adverse_displacement_pips=0,
        average_outcome_magnitude_pips=magnitude,
        direction_alignment_rate=alignment,
        sample_adequacy_flag="ADEQUATE",
        regime_observation_diagnostic="ok",
    )
