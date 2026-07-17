from sqre.h4_scenario_sensitive_state_review.findings import (
    profile_diagnostic,
    scenario_review_diagnostic,
    summary_diagnostic,
)


def test_findings_are_descriptive():
    assert "scenario-sensitive" in profile_diagnostic("HIGH_SCENARIO_SENSITIVITY")
    assert "elevated deviation" in scenario_review_diagnostic("HIGH_RECURRENT_DEVIATION")
    assert "selective aggregation review" in summary_diagnostic(1, 0, 3)
