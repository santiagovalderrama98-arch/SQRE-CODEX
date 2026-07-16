"""Classification rules for H4 scenario-sensitive state review."""

from __future__ import annotations

from collections import Counter

from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig


SENSITIVITY_PRIORITY = ["HIGH_SCENARIO_SENSITIVITY", "MODERATE_SCENARIO_SENSITIVITY", "LOW_SCENARIO_SENSITIVITY"]
RECURRENT_PRIORITY = ["HIGH_RECURRENT_DEVIATION", "MODERATE_RECURRENT_DEVIATION", "LOW_RECURRENT_DEVIATION"]


def scenario_sensitivity_class(
    high_deviation_count: int,
    moderate_deviation_count: int,
    dominant_deviation_class: str,
    profile_dispersion_class: str,
) -> str:
    if (
        high_deviation_count >= 2
        or dominant_deviation_class == "HIGH_DEVIATION"
        or profile_dispersion_class == "HIGH_DISPERSION"
    ):
        return "HIGH_SCENARIO_SENSITIVITY"
    if moderate_deviation_count >= 2 or dominant_deviation_class == "MODERATE_DEVIATION":
        return "MODERATE_SCENARIO_SENSITIVITY"
    return "LOW_SCENARIO_SENSITIVITY"


def near_aggregation_candidate_flag(
    total_sample_size: int,
    scenario_count: int,
    high_deviation_count: int,
    sensitivity_class: str,
    config: H4ScenarioSensitiveStateReviewConfig,
) -> str:
    if (
        total_sample_size >= config.minimum_total_sample_size
        and scenario_count >= config.minimum_scenario_count
        and high_deviation_count <= config.near_candidate_high_deviation_max
        and sensitivity_class != "HIGH_SCENARIO_SENSITIVITY"
    ):
        return "YES"
    return "NO"


def scenario_recurrent_deviation_class(high_deviation_ratio: float, config: H4ScenarioSensitiveStateReviewConfig) -> str:
    if high_deviation_ratio >= config.high_deviation_threshold:
        return "HIGH_RECURRENT_DEVIATION"
    if high_deviation_ratio >= config.moderate_deviation_threshold:
        return "MODERATE_RECURRENT_DEVIATION"
    return "LOW_RECURRENT_DEVIATION"


def h4_review_readiness_flag(reviewed_profiles: int, near_candidate_count: int) -> str:
    if reviewed_profiles > 0 and near_candidate_count > 0:
        return "READY_FOR_TARGETED_REVIEW"
    return "REQUIRES_SCENARIO_SENSITIVE_REVIEW"


def most_common(values: list[str], default: str = "") -> str:
    clean = [value for value in values if value]
    if not clean:
        return default
    counts = Counter(clean)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def dominant_sensitivity(classes: list[str]) -> str:
    return _dominant_with_priority(classes, SENSITIVITY_PRIORITY, "LOW_SCENARIO_SENSITIVITY")


def dominant_recurrent(classes: list[str]) -> str:
    return _dominant_with_priority(classes, RECURRENT_PRIORITY, "LOW_RECURRENT_DEVIATION")


def _dominant_with_priority(classes: list[str], priority: list[str], default: str) -> str:
    if not classes:
        return default
    counts = Counter(classes)
    return max(priority, key=lambda item: (counts.get(item, 0), -priority.index(item)))
