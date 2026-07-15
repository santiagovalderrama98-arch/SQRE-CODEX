from sqre.d1_regime_outcome_review.classification import (
    classify_condition_profiles,
    limited_coverage_profiles,
    low_sample_profiles,
    regime_sensitive_profiles,
    research_ready_profiles,
)
from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.models import ConditionProfileInput


def profile(
    *,
    sample: int = 40,
    regimes: int = 4,
    range_cv: float = 0.10,
    magnitude_cv: float = 0.12,
    sensitivity: str = "STABLE",
) -> ConditionProfileInput:
    return ConditionProfileInput(
        condition_type="STATE",
        condition_label="EXPANSION",
        forward_window=20,
        regime_count=regimes,
        regimes_present="A|B",
        scenario_count=4,
        total_sample_size=sample,
        average_sample_size_per_regime=10.0,
        average_forward_range_pips=22.0,
        average_outcome_magnitude_pips=8.0,
        average_direction_alignment_rate=0.6,
        forward_range_cv=range_cv,
        outcome_magnitude_cv=magnitude_cv,
        direction_alignment_cv=0.1,
        regime_sensitivity_flag=sensitivity,
    )


def test_classification_priority_low_sample_before_other_reviews():
    rows = classify_condition_profiles([profile(sample=5, regimes=1, range_cv=0.9)], D1RegimeOutcomeReviewConfig())

    assert rows[0].condition_research_class == "LOW_SAMPLE_REVIEW"
    assert low_sample_profiles(rows) == rows


def test_classification_priority_limited_coverage_before_regime_sensitive():
    rows = classify_condition_profiles([profile(sample=80, regimes=1, range_cv=0.9)], D1RegimeOutcomeReviewConfig())

    assert rows[0].condition_research_class == "LIMITED_COVERAGE_REVIEW"
    assert limited_coverage_profiles(rows) == rows


def test_classification_detects_research_ready_and_regime_sensitive_subsets():
    rows = classify_condition_profiles(
        [profile(), profile(sample=80, regimes=4, range_cv=0.50, sensitivity="")],
        D1RegimeOutcomeReviewConfig(),
    )

    assert [row.condition_research_class for row in rows] == [
        "RESEARCH_READY_DESCRIPTIVE",
        "REGIME_SENSITIVE_REVIEW",
    ]
    assert len(research_ready_profiles(rows)) == 1
    assert len(regime_sensitive_profiles(rows)) == 1
