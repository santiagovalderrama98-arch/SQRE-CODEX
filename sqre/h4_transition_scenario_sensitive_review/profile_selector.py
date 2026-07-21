"""Select scenario-sensitive H4 transition profiles for review."""

from __future__ import annotations

from collections import Counter

from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.models import ScenarioSensitiveTransitionProfileInput


SENSITIVITY_PRIORITY = [
    "HIGH_TRANSITION_SCENARIO_SENSITIVITY",
    "MODERATE_TRANSITION_SCENARIO_SENSITIVITY",
    "LOW_TRANSITION_SCENARIO_SENSITIVITY",
]


def select_review_profiles(
    profiles: list[ScenarioSensitiveTransitionProfileInput],
    config: H4TransitionScenarioSensitiveReviewConfig,
) -> list[ScenarioSensitiveTransitionProfileInput]:
    del config
    selected = [
        row
        for row in profiles
        if row.profile_type != "SAMPLE_CONSTRAINED_OBSERVATION" and _is_scenario_sensitive(row)
    ]
    return sorted(selected, key=lambda row: (row.condition_label, row.forward_window))


def focus_transition_flag(condition_label: str, config: H4TransitionScenarioSensitiveReviewConfig) -> str:
    focus = {transition.upper() for transition in config.focus_transitions}
    return "YES" if condition_label.upper() in focus else "NO"


def transition_sensitivity_class(
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
        return "HIGH_TRANSITION_SCENARIO_SENSITIVITY"
    if moderate_deviation_count >= 2 or dominant_deviation_class == "MODERATE_DEVIATION":
        return "MODERATE_TRANSITION_SCENARIO_SENSITIVITY"
    return "LOW_TRANSITION_SCENARIO_SENSITIVITY"


def near_aggregation_candidate_flag(
    total_sample_size: int,
    scenario_count: int,
    high_deviation_count: int,
    sensitivity_class: str,
    config: H4TransitionScenarioSensitiveReviewConfig,
) -> str:
    if (
        total_sample_size >= config.minimum_total_sample_size
        and scenario_count >= config.minimum_scenario_count
        and high_deviation_count <= config.near_candidate_high_deviation_max
        and sensitivity_class != "HIGH_TRANSITION_SCENARIO_SENSITIVITY"
    ):
        return "YES"
    return "NO"


def h4_review_readiness_flag(reviewed_profiles: int, near_candidate_count: int) -> str:
    if reviewed_profiles > 0 and near_candidate_count > 0:
        return "READY_FOR_TARGETED_TRANSITION_REVIEW"
    return "REQUIRES_TRANSITION_SCENARIO_SENSITIVE_REVIEW"


def most_common(values: list[str], default: str = "") -> str:
    clean = [value for value in values if value]
    if not clean:
        return default
    counts = Counter(clean)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def dominant_sensitivity(classes: list[str]) -> str:
    if not classes:
        return "LOW_TRANSITION_SCENARIO_SENSITIVITY"
    counts = Counter(classes)
    return max(SENSITIVITY_PRIORITY, key=lambda item: (counts.get(item, 0), -SENSITIVITY_PRIORITY.index(item)))


def _is_scenario_sensitive(row: ScenarioSensitiveTransitionProfileInput) -> bool:
    return (
        row.transition_profile_readiness_class == "SCENARIO_SENSITIVE_REVIEW"
        or row.profile_dispersion_class == "HIGH_DISPERSION"
        or row.high_deviation_scenario_count > 0
        or row.dominant_deviation_class == "HIGH_DEVIATION"
    )
