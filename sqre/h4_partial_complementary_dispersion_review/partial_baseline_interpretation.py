"""Final partial baseline interpretation matrix."""

from __future__ import annotations

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    PartialBaselineInterpretationRow,
    PartialSampleReviewRow,
    PartialSensitivityComplementReviewRow,
    PartialStateComplementReviewRow,
    PartialTransitionComplementReviewRow,
)


def build_partial_baseline_interpretation(
    sample: PartialSampleReviewRow,
    state_review: PartialStateComplementReviewRow,
    transition_review: PartialTransitionComplementReviewRow,
    sensitivity_review: PartialSensitivityComplementReviewRow,
    config: H4PartialComplementaryDispersionReviewConfig,
) -> PartialBaselineInterpretationRow:
    interpretation_class = classify_partial_baseline_interpretation(sample, sensitivity_review)
    return PartialBaselineInterpretationRow(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        baseline_scenario_count=config.baseline_scenario_count,
        coverage_ratio=sample.coverage_ratio,
        condition_profile_count=sample.condition_profile_count,
        sample_adequacy_class=sample.sample_adequacy_class,
        partial_comparison_class=sample.partial_comparison_class,
        state_consistency_class=state_review.partial_state_consistency_class,
        transition_consistency_class=transition_review.partial_transition_consistency_class,
        sensitivity_interpretation=sensitivity_review.partial_sensitivity_interpretation,
        partial_baseline_interpretation_class=interpretation_class,
        partial_baseline_interpretation_diagnostic=_diagnostic(interpretation_class),
        recommended_follow_up=_follow_up(interpretation_class),
    )


def classify_partial_baseline_interpretation(
    sample: PartialSampleReviewRow,
    sensitivity_review: PartialSensitivityComplementReviewRow,
) -> str:
    if sample.partial_sample_status == "PARTIAL_UNAVAILABLE":
        return "COMPLEMENTARY_EVIDENCE_UNAVAILABLE"
    interpretation = sensitivity_review.partial_sensitivity_interpretation
    if (
        interpretation == "PARTIAL_REINFORCES_SCENARIO_SENSITIVITY"
        and sample.sample_adequacy_class == "PARTIAL_SAMPLE_RESEARCH_USABLE"
    ):
        return "COMPLEMENTARY_EVIDENCE_SUPPORTS_PRIOR_H4_FINDINGS"
    if interpretation in {"PARTIAL_INTRODUCES_ELEVATED_DIVERGENCE", "PARTIAL_CONTRADICTS_PRIOR_SENSITIVITY"}:
        return "COMPLEMENTARY_EVIDENCE_DIVERGES_FROM_BASELINE"
    if interpretation == "PARTIAL_CONSISTENT_WITH_BASELINE_RANGE" or sample.coverage_ratio < 0.70:
        return "COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED"
    if interpretation == "PARTIAL_INCONCLUSIVE":
        return "COMPLEMENTARY_EVIDENCE_INCONCLUSIVE"
    return "COMPLEMENTARY_EVIDENCE_INCONCLUSIVE"


def _diagnostic(interpretation_class: str) -> str:
    diagnostics = {
        "COMPLEMENTARY_EVIDENCE_SUPPORTS_PRIOR_H4_FINDINGS": "Partial sample supports prior H4 research findings.",
        "COMPLEMENTARY_EVIDENCE_IS_CONSISTENT_BUT_LIMITED": "Partial sample is consistent but limited by coverage.",
        "COMPLEMENTARY_EVIDENCE_DIVERGES_FROM_BASELINE": "Partial sample differs from prior baseline range.",
        "COMPLEMENTARY_EVIDENCE_UNAVAILABLE": "Partial sample was unavailable for this review.",
    }
    return diagnostics.get(interpretation_class, "Partial sample interpretation is inconclusive.")


def _follow_up(interpretation_class: str) -> str:
    if interpretation_class == "COMPLEMENTARY_EVIDENCE_DIVERGES_FROM_BASELINE":
        return "Manual H4 data availability review."
    if interpretation_class == "COMPLEMENTARY_EVIDENCE_UNAVAILABLE":
        return "Provider history coverage review."
    return "H4 transition/state combined context review after partial sample interpretation."
