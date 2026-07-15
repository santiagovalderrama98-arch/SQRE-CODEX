from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.sensitivity import sensitivity_class


def test_sensitivity_class_prefers_valid_existing_flag():
    config = D1RegimeOutcomeReviewConfig()

    assert sensitivity_class("HIGH", 0.0, 0.0, config) == "HIGH"
    assert sensitivity_class("moderate", 0.0, 0.0, config) == "MODERATE"


def test_sensitivity_class_falls_back_to_cv_thresholds():
    config = D1RegimeOutcomeReviewConfig(moderate_sensitivity_threshold=0.2, high_sensitivity_threshold=0.35)

    assert sensitivity_class("", 0.40, 0.10, config) == "HIGH"
    assert sensitivity_class("", 0.10, 0.22, config) == "MODERATE"
    assert sensitivity_class("", 0.10, 0.19, config) == "STABLE"
