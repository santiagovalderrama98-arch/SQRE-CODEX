from sqre.h4_partial_complementary_dispersion_review.models import BaselineDispersionSnapshot, PartialSampleReviewRow
from sqre.h4_partial_complementary_dispersion_review.state_complement_review import (
    build_state_complement_review,
)


def test_state_complement_review_classifies_baseline_unavailable_safely():
    sample = PartialSampleReviewRow(
        candidate_id="eurusd_h4_period_5_partial",
        sample_label="PARTIAL_SAMPLE",
        coverage_ratio=0.5,
        run_status="COMPLETED",
        sample_adequacy_class="PARTIAL_SAMPLE_RESEARCH_USABLE",
        partial_comparison_class="CONSISTENT_WITH_BASELINE_RANGE",
        condition_profile_count=48,
        partial_sample_status="PARTIAL_VALIDATED",
        partial_sample_diagnostic="ok",
    )

    row = build_state_complement_review(sample, None, BaselineDispersionSnapshot())

    assert row.partial_state_consistency_class == "STATE_BASELINE_UNAVAILABLE"
