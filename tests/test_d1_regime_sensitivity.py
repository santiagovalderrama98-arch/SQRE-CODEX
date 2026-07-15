from sqre.d1_regime_normalized_research.config import D1RegimeResearchConfig
from sqre.d1_regime_normalized_research.regime_sensitivity import (
    cv,
    regime_coverage_flag,
    regime_sensitivity_flag,
    sample_adequacy_flag,
)


def test_cv_handles_zero_mean_safely():
    assert cv([0, 0, 0]) == 0.0


def test_flags_are_assigned_correctly():
    config = D1RegimeResearchConfig("test", "EURUSD", "D1", [])

    assert sample_adequacy_flag(5, config) == "ADEQUATE"
    assert sample_adequacy_flag(4, config) == "LOW_SAMPLE"
    assert regime_coverage_flag(2, config) == "SUFFICIENT"
    assert regime_coverage_flag(1, config) == "LIMITED"
    assert regime_sensitivity_flag(0.36, 0.1, config) == "HIGH"
    assert regime_sensitivity_flag(0.25, 0.1, config) == "MODERATE"
    assert regime_sensitivity_flag(0.1, 0.1, config) == "STABLE"
