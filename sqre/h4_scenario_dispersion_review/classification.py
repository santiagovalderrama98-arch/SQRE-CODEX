"""Classification rules for H4 scenario dispersion review."""

from __future__ import annotations

from collections import Counter

from sqre.h4_scenario_dispersion_review.config import H4ScenarioDispersionReviewConfig


DEVIATION_PRIORITY = ["HIGH_DEVIATION", "MODERATE_DEVIATION", "LOW_DEVIATION"]


def profile_dispersion_class(forward_range_cv: float, outcome_magnitude_cv: float, config: H4ScenarioDispersionReviewConfig) -> str:
    if forward_range_cv >= config.high_dispersion_threshold or outcome_magnitude_cv >= config.high_dispersion_threshold:
        return "HIGH_DISPERSION"
    if forward_range_cv >= config.moderate_dispersion_threshold or outcome_magnitude_cv >= config.moderate_dispersion_threshold:
        return "MODERATE_DISPERSION"
    return "STABLE_DESCRIPTIVE"


def dominant_deviation_class(classes: list[str]) -> str:
    if not classes:
        return "LOW_DEVIATION"
    counts = Counter(classes)
    return max(DEVIATION_PRIORITY, key=lambda item: (counts.get(item, 0), -DEVIATION_PRIORITY.index(item)))


def dispersion_driver_class(forward_range_cv: float, outcome_magnitude_cv: float, config: H4ScenarioDispersionReviewConfig) -> str:
    range_active = forward_range_cv >= config.moderate_dispersion_threshold
    magnitude_active = outcome_magnitude_cv >= config.moderate_dispersion_threshold
    if range_active and magnitude_active:
        return "MIXED_DRIVEN"
    if range_active and forward_range_cv > outcome_magnitude_cv:
        return "RANGE_DRIVEN"
    if magnitude_active and outcome_magnitude_cv > forward_range_cv:
        return "MAGNITUDE_DRIVEN"
    return "LOW_DISPERSION"


def profile_research_readiness_class(
    profile_type: str,
    total_sample_size: int,
    scenario_count: int,
    dispersion_class: str,
    high_deviation_count: int,
    dominant_deviation: str,
    config: H4ScenarioDispersionReviewConfig,
) -> str:
    if (
        profile_type == "SAMPLE_CONSTRAINED_OBSERVATION"
        or total_sample_size < config.minimum_total_sample_size
        or scenario_count < config.minimum_scenario_count
    ):
        return "SAMPLE_REVIEW"
    if (
        dispersion_class == "HIGH_DISPERSION"
        or high_deviation_count >= 2
        or dominant_deviation == "HIGH_DEVIATION"
    ):
        return "SCENARIO_SENSITIVE_REVIEW"
    if profile_type == "RESEARCH_READY" and dispersion_class in {"STABLE_DESCRIPTIVE", "MODERATE_DISPERSION"} and high_deviation_count <= 1:
        return "AGGREGATION_CANDIDATE"
    return "GENERAL_REVIEW"


def scenario_contribution_class(high_deviation_profile_ratio: float, config: H4ScenarioDispersionReviewConfig) -> str:
    if high_deviation_profile_ratio >= config.high_deviation_threshold:
        return "HIGH_CONTRIBUTION"
    if high_deviation_profile_ratio >= config.moderate_deviation_threshold:
        return "MODERATE_CONTRIBUTION"
    return "LOW_CONTRIBUTION"


def h4_aggregation_readiness_flag(aggregation_candidates: int, scenario_sensitive: int, research_ready: int) -> str:
    if aggregation_candidates > 0 and scenario_sensitive < research_ready:
        return "READY_FOR_SELECTIVE_AGGREGATION"
    return "REQUIRES_SCENARIO_DISPERSION_REVIEW"
