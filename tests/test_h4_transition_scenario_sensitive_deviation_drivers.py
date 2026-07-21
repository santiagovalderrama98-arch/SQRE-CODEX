from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.deviation_drivers import (
    primary_deviating_metric,
    primary_scenario_deviation_metric,
    scenario_deviation_intensity_class,
)
from sqre.h4_transition_scenario_sensitive_review.models import ScenarioComparisonInput


def test_primary_deviation_metric_uses_mixed_when_multiple_metrics_exceed_threshold():
    config = H4TransitionScenarioSensitiveReviewConfig()

    assert primary_deviating_metric(0.31, 0.30, 0.05, config) == "MIXED"
    assert primary_deviating_metric(0.31, 0.05, 0.02, config) == "RANGE"


def test_primary_scenario_deviation_metric_and_intensity():
    config = H4TransitionScenarioSensitiveReviewConfig()
    row = ScenarioComparisonInput(
        condition_label="A -> B",
        source_state="A",
        target_state="B",
        transition_family="X",
        forward_window=3,
        scenario_id="S1",
        forward_range_vs_profile_avg=0.05,
        outcome_magnitude_vs_profile_avg=0.42,
        direction_alignment_vs_profile_avg=0.01,
        scenario_deviation_class="HIGH_DEVIATION",
    )

    assert primary_scenario_deviation_metric(row, config) == "MAGNITUDE"
    assert scenario_deviation_intensity_class("HIGH_DEVIATION") == "HIGH"
    assert scenario_deviation_intensity_class("MODERATE_DEVIATION") == "MODERATE"
    assert scenario_deviation_intensity_class("LOW_DEVIATION") == "LOW"
