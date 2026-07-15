"""Condition quality classification."""

from __future__ import annotations

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.dispersion import dispersion_class
from sqre.d1_regime_outcome_review.models import ConditionProfileInput, ConditionQualityInventoryRow
from sqre.d1_regime_outcome_review.sample_adequacy import regime_coverage_class, sample_adequacy_class
from sqre.d1_regime_outcome_review.sensitivity import sensitivity_class


def classify_condition_profiles(
    profiles: list[ConditionProfileInput],
    config: D1RegimeOutcomeReviewConfig,
) -> list[ConditionQualityInventoryRow]:
    return [_classify(profile, config) for profile in profiles]


def research_ready_profiles(rows: list[ConditionQualityInventoryRow]) -> list[ConditionQualityInventoryRow]:
    return [row for row in rows if row.condition_research_class == "RESEARCH_READY_DESCRIPTIVE"]


def regime_sensitive_profiles(rows: list[ConditionQualityInventoryRow]) -> list[ConditionQualityInventoryRow]:
    return [row for row in rows if row.sensitivity_class == "HIGH" or row.dispersion_class == "HIGH"]


def low_sample_profiles(rows: list[ConditionQualityInventoryRow]) -> list[ConditionQualityInventoryRow]:
    return [row for row in rows if row.sample_adequacy_class == "LOW_SAMPLE"]


def limited_coverage_profiles(rows: list[ConditionQualityInventoryRow]) -> list[ConditionQualityInventoryRow]:
    return [row for row in rows if row.regime_coverage_class == "LIMITED"]


def _classify(profile: ConditionProfileInput, config: D1RegimeOutcomeReviewConfig) -> ConditionQualityInventoryRow:
    sample_class = sample_adequacy_class(profile.total_sample_size, config)
    coverage_class = regime_coverage_class(profile.regime_count, config)
    dispersion = dispersion_class(profile.forward_range_cv, profile.outcome_magnitude_cv, config)
    sensitivity = sensitivity_class(
        profile.regime_sensitivity_flag,
        profile.forward_range_cv,
        profile.outcome_magnitude_cv,
        config,
    )
    research_class = _research_class(sample_class, coverage_class, dispersion, sensitivity)
    return ConditionQualityInventoryRow(
        condition_type=profile.condition_type,
        condition_label=profile.condition_label,
        forward_window=profile.forward_window,
        regime_count=profile.regime_count,
        regimes_present=profile.regimes_present,
        scenario_count=profile.scenario_count,
        total_sample_size=profile.total_sample_size,
        average_sample_size_per_regime=profile.average_sample_size_per_regime,
        average_forward_range_pips=profile.average_forward_range_pips,
        average_outcome_magnitude_pips=profile.average_outcome_magnitude_pips,
        average_direction_alignment_rate=profile.average_direction_alignment_rate,
        forward_range_cv=profile.forward_range_cv,
        outcome_magnitude_cv=profile.outcome_magnitude_cv,
        direction_alignment_cv=profile.direction_alignment_cv,
        sample_adequacy_class=sample_class,
        regime_coverage_class=coverage_class,
        dispersion_class=dispersion,
        sensitivity_class=sensitivity,
        condition_research_class=research_class,
        condition_review_diagnostic=_diagnostic(research_class),
        recommended_follow_up=_follow_up(research_class),
    )


def _research_class(sample_class: str, coverage_class: str, dispersion: str, sensitivity: str) -> str:
    if sample_class == "LOW_SAMPLE":
        return "LOW_SAMPLE_REVIEW"
    if coverage_class == "LIMITED":
        return "LIMITED_COVERAGE_REVIEW"
    if sensitivity == "HIGH" or dispersion == "HIGH":
        return "REGIME_SENSITIVE_REVIEW"
    if coverage_class in {"SUFFICIENT", "FULL"} and dispersion in {"LOW", "MODERATE"} and sensitivity in {
        "STABLE",
        "MODERATE",
    }:
        return "RESEARCH_READY_DESCRIPTIVE"
    return "GENERAL_REVIEW"


def _diagnostic(research_class: str) -> str:
    return {
        "RESEARCH_READY_DESCRIPTIVE": (
            "Condition profile has adequate sample and acceptable regime dispersion for deeper descriptive review"
        ),
        "REGIME_SENSITIVE_REVIEW": "Condition profile requires regime-sensitive interpretation before deeper review",
        "LOW_SAMPLE_REVIEW": "Condition profile requires sample adequacy review",
        "LIMITED_COVERAGE_REVIEW": "Condition profile has limited regime coverage",
    }.get(research_class, "Condition profile requires further descriptive review")


def _follow_up(research_class: str) -> str:
    return {
        "RESEARCH_READY_DESCRIPTIVE": "Move condition profile to deeper descriptive review queue.",
        "REGIME_SENSITIVE_REVIEW": "Review regime-sensitive dispersion before aggregation.",
        "LOW_SAMPLE_REVIEW": "Review sample adequacy before deeper review.",
        "LIMITED_COVERAGE_REVIEW": "Review regime coverage before deeper review.",
    }.get(research_class, "Continue descriptive condition review.")
