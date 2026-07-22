from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import BaselineDispersionSnapshot, PartialSampleReviewRow
from sqre.h4_partial_complementary_dispersion_review.sensitivity_complement_review import (
    build_sensitivity_complement_review,
)


def _sample(comparison: str, count: int = 48) -> PartialSampleReviewRow:
    return PartialSampleReviewRow(
        candidate_id="eurusd_h4_period_5_partial",
        sample_label="PARTIAL_SAMPLE",
        coverage_ratio=0.5,
        run_status="COMPLETED",
        sample_adequacy_class="PARTIAL_SAMPLE_RESEARCH_USABLE",
        partial_comparison_class=comparison,
        condition_profile_count=count,
        partial_sample_status="PARTIAL_VALIDATED",
        partial_sample_diagnostic="ok",
    )


def test_sensitivity_review_classifies_reinforces_scenario_sensitivity():
    baseline = BaselineDispersionSnapshot(
        scenario_sensitive_profile="HIGH_TRANSITION_SCENARIO_SENSITIVITY",
        high_sensitivity_profile_count=10,
    )

    row = build_sensitivity_complement_review(
        _sample("CONSISTENT_WITH_BASELINE_RANGE"),
        baseline,
        H4PartialComplementaryDispersionReviewConfig(),
    )

    assert row.partial_sensitivity_interpretation == "PARTIAL_REINFORCES_SCENARIO_SENSITIVITY"


def test_sensitivity_review_classifies_consistent_with_baseline_range():
    baseline = BaselineDispersionSnapshot(scenario_sensitive_profile="MODERATE_SCENARIO_SENSITIVITY")

    row = build_sensitivity_complement_review(
        _sample("CONSISTENT_WITH_BASELINE_RANGE", 4),
        baseline,
        H4PartialComplementaryDispersionReviewConfig(),
    )

    assert row.partial_sensitivity_interpretation == "PARTIAL_CONSISTENT_WITH_BASELINE_RANGE"
