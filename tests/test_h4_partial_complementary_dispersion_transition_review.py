from sqre.h4_partial_complementary_dispersion_review.models import (
    BaselineDispersionSnapshot,
    PartialSampleReviewRow,
    PartialTransitionSnapshot,
)
from sqre.h4_partial_complementary_dispersion_review.transition_complement_review import (
    build_transition_complement_review,
)


def test_transition_complement_review_classifies_consistency_correctly():
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
    baseline = BaselineDispersionSnapshot(
        transition_dispersion_profile="MIXED_DRIVEN",
        transition_readiness_flag="RESEARCH_REVIEW_READY",
    )
    transition = PartialTransitionSnapshot(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        partial_most_common_transition="A_TO_B",
        partial_unique_transition_count=4,
    )

    row = build_transition_complement_review(sample, transition, baseline)

    assert row.partial_transition_consistency_class == "TRANSITION_CONSISTENT_WITH_BASELINE"
    assert row.partial_unique_transition_count == 4
