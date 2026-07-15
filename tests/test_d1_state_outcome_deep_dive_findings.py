from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.findings import (
    outcome_profile_diagnostic,
    regime_comparison_diagnostic,
    regime_deviation_class,
    stability_class,
)


def test_findings_are_descriptive_and_non_ranking():
    config = D1StateOutcomeDeepDiveConfig()

    findings = [
        stability_class(0.1, 0.1, config),
        regime_deviation_class(0.1, config),
        outcome_profile_diagnostic("RESEARCH_READY", "STABLE_DESCRIPTIVE"),
        regime_comparison_diagnostic("LOW_DEVIATION"),
    ]

    joined = " ".join(findings).lower()
    assert "ranking" not in joined
    assert "best timeframe" not in joined
    assert "trade signal" not in joined


def test_stability_class_uses_dispersion_thresholds():
    config = D1StateOutcomeDeepDiveConfig(moderate_dispersion_threshold=0.2, high_dispersion_threshold=0.35)

    assert stability_class(0.36, 0.1, config) == "HIGH_DISPERSION"
    assert stability_class(0.1, 0.25, config) == "MODERATE_DISPERSION"
    assert stability_class(0.1, 0.1, config) == "STABLE_DESCRIPTIVE"
