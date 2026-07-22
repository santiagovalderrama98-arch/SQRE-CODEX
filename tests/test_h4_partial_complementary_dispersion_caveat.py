from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import PartialSampleReviewRow
from sqre.h4_partial_complementary_dispersion_review.sample_caveat_review import build_sample_caveat_review


def _sample(coverage: float, adequacy: str = "PARTIAL_SAMPLE_RESEARCH_USABLE") -> PartialSampleReviewRow:
    return PartialSampleReviewRow(
        candidate_id="eurusd_h4_period_5_partial",
        sample_label="PARTIAL_SAMPLE",
        coverage_ratio=coverage,
        run_status="COMPLETED",
        sample_adequacy_class=adequacy,
        partial_comparison_class="CONSISTENT_WITH_BASELINE_RANGE",
        condition_profile_count=48,
        partial_sample_status="PARTIAL_VALIDATED",
        partial_sample_diagnostic="ok",
    )


def test_caveat_review_classifies_acceptable_complementary_review():
    row = build_sample_caveat_review(_sample(0.5), H4PartialComplementaryDispersionReviewConfig())

    assert row.partial_sample_caveat_class == "PARTIAL_SAMPLE_ACCEPTABLE_FOR_COMPLEMENTARY_REVIEW"


def test_caveat_review_classifies_limited_interpretation():
    row = build_sample_caveat_review(
        _sample(0.55, adequacy="PARTIAL_SAMPLE_LIMITED"),
        H4PartialComplementaryDispersionReviewConfig(),
    )

    assert row.partial_sample_caveat_class == "PARTIAL_SAMPLE_LIMITED_INTERPRETATION_REQUIRED"
