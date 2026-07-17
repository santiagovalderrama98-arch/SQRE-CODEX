from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.findings import scenario_comparison_diagnostic, stability_class


def test_findings_are_descriptive():
    assert stability_class(0.4, 0.1, H4TransitionOutcomeDeepDiveConfig()) == "HIGH_DISPERSION"
    assert "Scenario-period observation" in scenario_comparison_diagnostic("LOW_DEVIATION")
