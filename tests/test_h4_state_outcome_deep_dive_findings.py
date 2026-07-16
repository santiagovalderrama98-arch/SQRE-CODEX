from sqre.h4_state_outcome_deep_dive.config import H4StateOutcomeDeepDiveConfig
from sqre.h4_state_outcome_deep_dive.findings import (
    outcome_profile_diagnostic,
    scenario_deviation_class,
    scenario_observation_diagnostic,
    stability_class,
)


def test_findings_classify_dispersion_and_diagnostics():
    config = H4StateOutcomeDeepDiveConfig()

    assert stability_class(0.1, 0.1, config) == "STABLE_DESCRIPTIVE"
    assert stability_class(0.25, 0.1, config) == "MODERATE_DISPERSION"
    assert stability_class(0.4, 0.1, config) == "HIGH_DISPERSION"
    assert scenario_deviation_class(0.4, config) == "HIGH_DEVIATION"
    assert "limited sample size" in scenario_observation_diagnostic("RESEARCH_READY", 3, config)
    assert "requires sample adequacy review" in outcome_profile_diagnostic("SAMPLE_CONSTRAINED_OBSERVATION", "STABLE")
