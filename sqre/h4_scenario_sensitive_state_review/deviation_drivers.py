"""Deviation driver helpers for H4 scenario-sensitive review."""

from __future__ import annotations

from sqre.h4_scenario_sensitive_state_review.config import H4ScenarioSensitiveStateReviewConfig
from sqre.h4_scenario_sensitive_state_review.models import ScenarioComparisonInput


def primary_deviating_metric(
    forward_range_cv: float,
    outcome_magnitude_cv: float,
    direction_alignment_dispersion: float,
    config: H4ScenarioSensitiveStateReviewConfig,
) -> str:
    return _primary_metric(
        {
            "RANGE": abs(forward_range_cv),
            "MAGNITUDE": abs(outcome_magnitude_cv),
            "ALIGNMENT": abs(direction_alignment_dispersion),
        },
        config.moderate_deviation_threshold,
        use_active_threshold=True,
    )


def primary_scenario_deviation_metric(row: ScenarioComparisonInput, config: H4ScenarioSensitiveStateReviewConfig) -> str:
    return _primary_metric(
        {
            "RANGE": abs(row.forward_range_vs_profile_avg),
            "MAGNITUDE": abs(row.outcome_magnitude_vs_profile_avg),
            "ALIGNMENT": abs(row.direction_alignment_vs_profile_avg),
        },
        config.moderate_deviation_threshold,
        use_active_threshold=False,
    )


def scenario_deviation_intensity_class(scenario_deviation_class: str) -> str:
    if scenario_deviation_class == "HIGH_DEVIATION":
        return "HIGH"
    if scenario_deviation_class == "MODERATE_DEVIATION":
        return "MODERATE"
    return "LOW"


def _primary_metric(values: dict[str, float], moderate_threshold: float, use_active_threshold: bool) -> str:
    if not values or max(values.values()) <= 0:
        return "MIXED"
    active_count = sum(1 for value in values.values() if value >= moderate_threshold)
    if use_active_threshold and active_count >= 2:
        return "MIXED"
    ordered = sorted(values.items(), key=lambda item: item[1], reverse=True)
    highest_name, highest_value = ordered[0]
    second_value = ordered[1][1] if len(ordered) > 1 else 0.0
    if highest_value and abs(highest_value - second_value) <= abs(highest_value) * 0.10:
        return "MIXED"
    return highest_name
