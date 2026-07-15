from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.sample_adequacy import ratio, regime_coverage_class, sample_adequacy_class


def test_sample_adequacy_class_uses_minimum_total_sample_size():
    config = D1RegimeOutcomeReviewConfig(minimum_total_sample_size=20)

    assert sample_adequacy_class(20, config) == "ADEQUATE"
    assert sample_adequacy_class(19, config) == "LOW_SAMPLE"


def test_regime_coverage_class_uses_configured_counts():
    config = D1RegimeOutcomeReviewConfig(minimum_regime_count=2, full_regime_count=4)

    assert regime_coverage_class(4, config) == "FULL"
    assert regime_coverage_class(2, config) == "SUFFICIENT"
    assert regime_coverage_class(1, config) == "LIMITED"


def test_ratio_handles_zero_denominator():
    assert ratio(4, 8) == 0.5
    assert ratio(4, 0) == 0.0
