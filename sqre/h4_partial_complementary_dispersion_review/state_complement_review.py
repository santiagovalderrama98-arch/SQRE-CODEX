"""State complement review for partial H4 sample."""

from __future__ import annotations

from sqre.h4_partial_complementary_dispersion_review.models import (
    BaselineDispersionSnapshot,
    PartialSampleReviewRow,
    PartialStateComplementReviewRow,
    PartialStructureStateSnapshot,
)


def build_state_complement_review(
    sample: PartialSampleReviewRow,
    structure_state: PartialStructureStateSnapshot | None,
    baseline: BaselineDispersionSnapshot,
) -> PartialStateComplementReviewRow:
    state_snapshot = structure_state or PartialStructureStateSnapshot(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        partial_state_profile="NO_STATE_DATA",
        partial_unique_state_count=0,
        partial_most_common_state="NO_STATE_DATA",
    )
    review_class = classify_state_consistency(sample, baseline)
    return PartialStateComplementReviewRow(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        partial_state_profile=state_snapshot.partial_state_profile,
        partial_unique_state_count=state_snapshot.partial_unique_state_count,
        partial_most_common_state=state_snapshot.partial_most_common_state,
        baseline_state_dispersion_profile=baseline.state_dispersion_profile,
        baseline_state_readiness_flag=baseline.state_readiness_flag,
        partial_state_consistency_class=review_class,
        partial_state_diagnostic=_diagnostic(review_class),
    )


def classify_state_consistency(
    sample: PartialSampleReviewRow,
    baseline: BaselineDispersionSnapshot,
) -> str:
    if baseline.state_dispersion_profile == "BASELINE_UNAVAILABLE":
        return "STATE_BASELINE_UNAVAILABLE"
    if sample.partial_sample_status != "PARTIAL_VALIDATED":
        return "STATE_INCONCLUSIVE_DUE_TO_PARTIAL_COVERAGE"
    comparison = sample.partial_comparison_class.upper()
    if comparison == "CONSISTENT_WITH_BASELINE_RANGE":
        return "STATE_CONSISTENT_WITH_BASELINE"
    if comparison in {"ELEVATED_VS_BASELINE", "LOWER_THAN_BASELINE", "MATERIAL_DEVIATION_FROM_BASELINE"}:
        return "STATE_DIVERGENT_FROM_BASELINE"
    return "STATE_INCONCLUSIVE_DUE_TO_PARTIAL_COVERAGE"


def _diagnostic(review_class: str) -> str:
    diagnostics = {
        "STATE_CONSISTENT_WITH_BASELINE": "Partial state context is consistent with prior H4 state dispersion.",
        "STATE_DIVERGENT_FROM_BASELINE": "Partial state context differs from prior H4 state dispersion.",
        "STATE_BASELINE_UNAVAILABLE": "Baseline state dispersion file was unavailable.",
    }
    return diagnostics.get(review_class, "Partial state context requires limited interpretation.")
