from sqre.calibration_review.config import CalibrationReviewConfig
from sqre.calibration_review.metrics import build_calibration_metrics
from sqre.calibration_review.models import ValidationScenarioSummary


def _scenario(**overrides) -> ValidationScenarioSummary:
    values = {
        "scenario_id": "eurusd_m5_period_1",
        "status": "COMPLETED",
        "symbol": "EURUSD",
        "timeframe": "M5",
        "ohlc_rows": 1000,
        "max_structure_duration_seconds": 100,
        "structures_detected": 10,
        "average_structure_duration": 50.0,
        "states_generated": 10,
        "unique_states": 6,
        "most_common_state": "DIRECTIONAL_DISPLACEMENT",
        "directional_displacement_count": 4,
        "directional_expansion_count": 2,
        "directional_drift_count": 1,
        "volatile_rotation_count": 1,
        "complex_consolidation_count": 1,
        "neutral_compression_count": 1,
        "low_quality_structure_count": 1,
        "unclassified_count": 1,
        "transitions_generated": 8,
        "unique_transitions": 5,
        "state_change_rate": 0.4,
        "direction_change_rate": 0.3,
        "average_transition_stability": 0.8,
        "conditions_evaluated": 20,
        "low_sample_conditions_research": 5,
        "price_outcome_summary_rows": 10,
        "low_sample_conditions_price_outcome": 2,
        "average_forward_range_pips": 12.5,
        "average_outcome_magnitude_pips": 8.0,
        "direction_alignment_rate": 0.55,
        "average_forward_close_return_pips": 1.2,
    }
    values.update(overrides)
    return ValidationScenarioSummary(**values)


def test_build_calibration_metrics_calculates_ratios():
    rows = build_calibration_metrics([_scenario()], CalibrationReviewConfig())

    row = rows[0]
    assert row.duration_utilization_ratio == 0.5
    assert row.most_common_state_ratio == 0.4
    assert row.directional_state_ratio == 0.7
    assert row.compression_consolidation_ratio == 0.2
    assert row.volatile_rotation_ratio == 0.1
    assert row.low_quality_rate == 0.1
    assert row.research_low_sample_rate == 0.25
    assert row.price_outcome_low_sample_rate == 0.2
    assert row.calibration_status == "OK"


def test_build_calibration_metrics_sets_review_status_for_combined_low_sample_flags():
    rows = build_calibration_metrics(
        [
            _scenario(
                low_sample_conditions_research=11,
                conditions_evaluated=20,
                low_sample_conditions_price_outcome=6,
                price_outcome_summary_rows=10,
            )
        ],
        CalibrationReviewConfig(),
    )

    assert rows[0].high_research_low_sample_flag is True
    assert rows[0].high_price_outcome_low_sample_flag is True
    assert rows[0].calibration_status == "REVIEW"


def test_build_calibration_metrics_marks_incomplete_scenario_not_available():
    rows = build_calibration_metrics([_scenario(status="MISSING_INPUT")], CalibrationReviewConfig())

    assert rows[0].calibration_status == "NOT_AVAILABLE"


def test_build_calibration_metrics_handles_zero_denominators():
    rows = build_calibration_metrics(
        [
            _scenario(
                max_structure_duration_seconds=0,
                states_generated=0,
                conditions_evaluated=0,
                price_outcome_summary_rows=0,
            )
        ],
        CalibrationReviewConfig(),
    )

    row = rows[0]
    assert row.duration_utilization_ratio == 0.0
    assert row.most_common_state_ratio == 0.0
    assert row.research_low_sample_rate == 0.0
