from sqre.h4_transition_scenario_dispersion_review.classification import (
    dispersion_driver_class,
    dominant_deviation_class,
    profile_dispersion_class,
    transition_profile_readiness_class,
)
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig


def test_dominant_deviation_tie_priority_prefers_high():
    assert dominant_deviation_class(["LOW_DEVIATION", "MODERATE_DEVIATION", "HIGH_DEVIATION"]) == "HIGH_DEVIATION"


def test_dispersion_driver_class_uses_range_magnitude_and_mixed_rules():
    config = H4TransitionScenarioDispersionReviewConfig()

    assert dispersion_driver_class(0.25, 0.1, config) == "RANGE_DRIVEN"
    assert dispersion_driver_class(0.1, 0.25, config) == "MAGNITUDE_DRIVEN"
    assert dispersion_driver_class(0.25, 0.25, config) == "MIXED_DRIVEN"
    assert dispersion_driver_class(0.1, 0.1, config) == "LOW_DISPERSION"


def test_research_readiness_priority_is_sample_then_scenario_then_candidate():
    config = H4TransitionScenarioDispersionReviewConfig()

    assert profile_dispersion_class(0.4, 0.1, config) == "HIGH_DISPERSION"
    assert (
        transition_profile_readiness_class("SAMPLE_CONSTRAINED_OBSERVATION", 5, 1, "HIGH_DISPERSION", 3, "HIGH_DEVIATION", config)
        == "SAMPLE_REVIEW"
    )
    assert (
        transition_profile_readiness_class("RESEARCH_READY", 90, 3, "HIGH_DISPERSION", 0, "LOW_DEVIATION", config)
        == "SCENARIO_SENSITIVE_REVIEW"
    )
    assert (
        transition_profile_readiness_class("RESEARCH_READY", 90, 3, "MODERATE_DISPERSION", 1, "LOW_DEVIATION", config)
        == "AGGREGATION_CANDIDATE"
    )
