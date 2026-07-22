"""Scenario sensitivity complement review for partial H4 sample."""

from __future__ import annotations

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    BaselineDispersionSnapshot,
    PartialSampleReviewRow,
    PartialSensitivityComplementReviewRow,
)


def build_sensitivity_complement_review(
    sample: PartialSampleReviewRow,
    baseline: BaselineDispersionSnapshot,
    config: H4PartialComplementaryDispersionReviewConfig,
) -> PartialSensitivityComplementReviewRow:
    interpretation = classify_sensitivity_interpretation(sample, baseline, config)
    return PartialSensitivityComplementReviewRow(
        candidate_id=sample.candidate_id,
        sample_label=sample.sample_label,
        baseline_scenario_sensitive_profile=baseline.scenario_sensitive_profile,
        baseline_high_sensitivity_profile_count=baseline.high_sensitivity_profile_count,
        baseline_near_aggregation_candidate_count=baseline.near_aggregation_candidate_count,
        partial_comparison_class=sample.partial_comparison_class,
        partial_condition_profile_count=sample.condition_profile_count,
        partial_sensitivity_interpretation=interpretation,
        partial_sensitivity_diagnostic=_diagnostic(interpretation),
    )


def classify_sensitivity_interpretation(
    sample: PartialSampleReviewRow,
    baseline: BaselineDispersionSnapshot,
    config: H4PartialComplementaryDispersionReviewConfig,
) -> str:
    comparison = sample.partial_comparison_class.upper()
    profile = baseline.scenario_sensitive_profile.upper()
    has_minimum_profiles = sample.condition_profile_count >= config.minimum_condition_profile_count
    high_profile = profile in {"HIGH_TRANSITION_SCENARIO_SENSITIVITY", "HIGH_SCENARIO_SENSITIVITY"}

    if (
        high_profile
        and comparison == "CONSISTENT_WITH_BASELINE_RANGE"
        and has_minimum_profiles
    ):
        return "PARTIAL_REINFORCES_SCENARIO_SENSITIVITY"
    if baseline.high_sensitivity_profile_count > 0 and comparison == "LOWER_THAN_BASELINE" and has_minimum_profiles:
        return "PARTIAL_CONTRADICTS_PRIOR_SENSITIVITY"
    if comparison == "ELEVATED_VS_BASELINE":
        return "PARTIAL_INTRODUCES_ELEVATED_DIVERGENCE"
    if comparison == "CONSISTENT_WITH_BASELINE_RANGE" and sample.condition_profile_count > 0:
        return "PARTIAL_CONSISTENT_WITH_BASELINE_RANGE"
    return "PARTIAL_INCONCLUSIVE"


def _diagnostic(interpretation: str) -> str:
    diagnostics = {
        "PARTIAL_REINFORCES_SCENARIO_SENSITIVITY": "Partial sample supports prior scenario-sensitive interpretation.",
        "PARTIAL_CONSISTENT_WITH_BASELINE_RANGE": "Partial sample is consistent with prior baseline range.",
        "PARTIAL_INTRODUCES_ELEVATED_DIVERGENCE": "Partial sample introduces elevated divergence from prior baseline range.",
        "PARTIAL_CONTRADICTS_PRIOR_SENSITIVITY": "Partial sample differs from prior scenario-sensitive interpretation.",
    }
    return diagnostics.get(interpretation, "Partial sample sensitivity interpretation is inconclusive.")
