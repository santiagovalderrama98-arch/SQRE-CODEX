from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.deviation_drivers import (
    primary_deviating_metric,
    primary_scenario_deviation_metric,
    scenario_deviation_intensity_class,
)
from sqre.h4_scenario_sensitive_state_review.models import ScenarioComparisonInput


def test_primary_deviation_metric_supports_range_magnitude_alignment_and_mixed():
    config = H4ScenarioSensitiveStateReviewConfig()

    assert primary_deviating_metric(0.40, 0.10, 0.05, config) == "RANGE"
    assert primary_deviating_metric(0.10, 0.40, 0.05, config) == "MAGNITUDE"
    assert primary_deviating_metric(0.10, 0.05, 0.40, config) == "ALIGNMENT"
    assert primary_deviating_metric(0.30, 0.28, 0.05, config) == "MIXED"


def test_scenario_deviation_metric_and_intensity():
    config = H4ScenarioSensitiveStateReviewConfig()
    row = ScenarioComparisonInput(
        condition_label="DIRECTIONAL_EXPANSION",
        forward_window=3,
        scenario_id="S1",
        sample_size=30,
        forward_range_vs_profile_avg=5,
        outcome_magnitude_vs_profile_avg=1,
        direction_alignment_vs_profile_avg=0.1,
        scenario_deviation_class="HIGH_DEVIATION",
    )

    assert primary_scenario_deviation_metric(row, config) == "RANGE"
    assert scenario_deviation_intensity_class(row.scenario_deviation_class) == "HIGH"
