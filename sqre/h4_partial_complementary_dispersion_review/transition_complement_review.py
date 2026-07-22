"""Transition complement review for partial H4 sample."""

from __future__ import annotations

from sqre.h4_partial_complementary_dispersion_review.models import (
    BaselineDispersionSnapshot,
    PartialSampleReviewRow,
    PartialTransitionComplementReviewRow,
    PartialTransitionSnapshot,
)


def build_transition_complement_review(
    sample: PartialSampleReviewRow,
    transition: PartialTransitionSnapshot | None,
    baseline: BaselineDispersionSnapshot,
) -> PartialTransitionComplementReviewRow:
    transition_snapshot = transition or PartialTransitionSnapshot(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        partial_most_common_transition="NO_TRANSITION_DATA",
        partial_unique_transition_count=0,
    )
    review_class = classify_transition_consistency(sample, baseline)
    return PartialTransitionComplementReviewRow(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        partial_most_common_transition=transition_snapshot.partial_most_common_transition,
        partial_unique_transition_count=transition_snapshot.partial_unique_transition_count,
        baseline_transition_dispersion_profile=baseline.transition_dispersion_profile,
        baseline_transition_readiness_flag=baseline.transition_readiness_flag,
        partial_transition_consistency_class=review_class,
        partial_transition_diagnostic=_diagnostic(review_class),
    )


def classify_transition_consistency(
    sample: PartialSampleReviewRow,
    baseline: BaselineDispersionSnapshot,
) -> str:
    if baseline.transition_dispersion_profile == "BASELINE_UNAVAILABLE":
        return "TRANSITION_BASELINE_UNAVAILABLE"
    if sample.partial_sample_status != "PARTIAL_VALIDATED":
        return "TRANSITION_INCONCLUSIVE_DUE_TO_PARTIAL_COVERAGE"
    comparison = sample.partial_comparison_class.upper()
    if comparison == "CONSISTENT_WITH_BASELINE_RANGE":
        return "TRANSITION_CONSISTENT_WITH_BASELINE"
    if comparison in {"ELEVATED_VS_BASELINE", "LOWER_THAN_BASELINE", "MATERIAL_DEVIATION_FROM_BASELINE"}:
        return "TRANSITION_DIVERGENT_FROM_BASELINE"
    return "TRANSITION_INCONCLUSIVE_DUE_TO_PARTIAL_COVERAGE"


def _diagnostic(review_class: str) -> str:
    diagnostics = {
        "TRANSITION_CONSISTENT_WITH_BASELINE": "Partial transition context is consistent with prior H4 transition dispersion.",
        "TRANSITION_DIVERGENT_FROM_BASELINE": "Partial transition context differs from prior H4 transition dispersion.",
        "TRANSITION_BASELINE_UNAVAILABLE": "Baseline transition dispersion file was unavailable.",
    }
    return diagnostics.get(review_class, "Partial transition context requires limited interpretation.")
