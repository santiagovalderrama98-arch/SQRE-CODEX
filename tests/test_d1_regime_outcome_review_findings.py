from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.findings import d1_review_diagnostic


def test_d1_review_diagnostic_identifies_usable_subset():
    diagnostic = d1_review_diagnostic(
        input_count=10,
        research_ready_count=6,
        regime_sensitive_count=2,
        low_sample_count=1,
        config=D1RegimeOutcomeReviewConfig(),
    )

    assert diagnostic == "D1 has a usable descriptive condition subset for deeper research"


def test_d1_review_diagnostic_identifies_sample_constrained_universe():
    diagnostic = d1_review_diagnostic(
        input_count=10,
        research_ready_count=2,
        regime_sensitive_count=1,
        low_sample_count=5,
        config=D1RegimeOutcomeReviewConfig(low_sample_share_threshold=0.5),
    )

    assert diagnostic == "D1 condition universe remains sample constrained"


def test_d1_review_diagnostic_identifies_regime_sensitive_review():
    diagnostic = d1_review_diagnostic(
        input_count=10,
        research_ready_count=2,
        regime_sensitive_count=4,
        low_sample_count=1,
        config=D1RegimeOutcomeReviewConfig(),
    )

    assert diagnostic == "D1 condition outcomes require regime-sensitive review before aggregation"
