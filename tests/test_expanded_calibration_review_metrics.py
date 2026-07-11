from sqre.expanded_calibration_review.config import ExpandedCalibrationReviewConfig
from sqre.expanded_calibration_review.metrics import build_timeframe_metrics
from sqre.expanded_calibration_review.models import ExpandedValidationScenarioSummary


def test_metrics_compute_grouped_timeframe_rows():
    rows = build_timeframe_metrics(
        [
            _scenario("h4_a", "H4", structures=10, states=10, unique_states=5, complex_count=2),
            _scenario("h4_b", "H4", structures=14, states=14, unique_states=5, complex_count=3),
            _scenario("d1_a", "D1", structures=4, states=4, unique_states=2, forward_range=50),
        ],
        ExpandedCalibrationReviewConfig(),
    )

    by_tf = {row.timeframe: row for row in rows}
    assert by_tf["H4"].scenario_count == 2
    assert by_tf["H4"].total_ohlc_rows == 2000
    assert by_tf["H4"].structure_count_range == 4
    assert by_tf["D1"].scenario_count == 1


def test_cv_calculations_handle_zero_mean():
    rows = build_timeframe_metrics(
        [_scenario("zero_a", "M5", structures=0, states=0), _scenario("zero_b", "M5", structures=0, states=0)],
        ExpandedCalibrationReviewConfig(),
    )

    row = rows[0]
    assert row.structure_count_cv == 0.0
    assert row.structure_duration_cv == 0.0
    assert row.forward_range_cv == 0.0


def test_directional_and_complex_ratios_work():
    rows = build_timeframe_metrics(
        [
            _scenario(
                "m5_a",
                "M5",
                structures=10,
                states=10,
                unique_states=8,
                displacement=3,
                expansion=2,
                drift=1,
                complex_count=5,
            )
        ],
        ExpandedCalibrationReviewConfig(),
    )

    row = rows[0]
    assert row.average_directional_state_ratio == 0.6
    assert row.average_complex_consolidation_ratio == 0.5
    assert row.state_diversity_flag == "HIGH_DIVERSITY"
    assert row.diagnostic_profile == "Microstructure/consolidation-heavy timeframe"


def test_flags_are_assigned_correctly():
    rows = build_timeframe_metrics(
        [
            _scenario("h1_a", "H1", structures=10, states=10, unique_states=7, low_sample_research=70),
            _scenario("h1_b", "H1", structures=20, states=20, unique_states=7, low_sample_research=60),
        ],
        ExpandedCalibrationReviewConfig(high_structure_variation_threshold=0.10),
    )

    row = rows[0]
    assert row.structural_stability_flag == "VARIABLE"
    assert row.state_diversity_flag == "HIGH_DIVERSITY"
    assert row.low_sample_pressure_flag == "HIGH"


def _scenario(
    scenario_id: str,
    timeframe: str,
    *,
    structures: int,
    states: int,
    unique_states: int = 4,
    forward_range: float = 20.0,
    displacement: int = 1,
    expansion: int = 1,
    drift: int = 0,
    complex_count: int = 1,
    low_sample_research: int = 0,
) -> ExpandedValidationScenarioSummary:
    return ExpandedValidationScenarioSummary(
        scenario_id=scenario_id,
        timeframe=timeframe,
        ohlc_rows=1000,
        structures_detected=structures,
        average_structure_duration=float(structures),
        states_generated=states,
        unique_states=unique_states,
        most_common_state="COMPLEX_CONSOLIDATION",
        directional_displacement_count=displacement,
        directional_expansion_count=expansion,
        directional_drift_count=drift,
        complex_consolidation_count=complex_count,
        average_forward_range_pips=forward_range,
        low_sample_conditions_research=low_sample_research,
    )
