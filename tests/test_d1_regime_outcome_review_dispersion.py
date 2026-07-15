from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.dispersion import dispersion_class, mean


def test_dispersion_class_uses_highest_cv_signal():
    config = D1RegimeOutcomeReviewConfig(moderate_dispersion_threshold=0.2, high_dispersion_threshold=0.35)

    assert dispersion_class(0.36, 0.10, config) == "HIGH"
    assert dispersion_class(0.10, 0.22, config) == "MODERATE"
    assert dispersion_class(0.10, 0.19, config) == "LOW"


def test_mean_returns_zero_for_empty_values():
    assert mean([1.0, 3.0]) == 2.0
    assert mean([]) == 0.0
