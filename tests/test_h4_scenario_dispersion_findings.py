from sqre.h4_scenario_dispersion_review.findings import (
    h4_summary_diagnostic,
    scenario_diagnostic,
    state_diagnostic,
    window_diagnostic,
)


def test_findings_are_descriptive_and_non_ordering():
    assert "selective subset" in h4_summary_diagnostic(1, 2, 1)
    assert "elevated deviation" in scenario_diagnostic("HIGH_CONTRIBUTION")
    assert "primarily scenario-sensitive" in state_diagnostic(3, 0, 2, 0)
    assert "elevated dispersion" in window_diagnostic(3, 2, 0, 1)
