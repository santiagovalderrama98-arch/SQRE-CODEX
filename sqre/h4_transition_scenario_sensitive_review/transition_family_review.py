"""Transition-family sensitivity summaries."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_transition_scenario_sensitive_review.findings import (
    group_follow_up,
    transition_family_diagnostic,
)
from sqre.h4_transition_scenario_sensitive_review.models import (
    ProfileReviewRow,
    TransitionGroupSensitivitySummary,
)
from sqre.h4_transition_scenario_sensitive_review.profile_selector import most_common


def build_transition_family_sensitivity_summary(
    rows: list[ProfileReviewRow],
) -> list[TransitionGroupSensitivitySummary]:
    grouped: dict[str, list[ProfileReviewRow]] = defaultdict(list)
    for row in rows:
        grouped[row.transition_family].append(row)
    return [_build_summary(family, items, "family") for family, items in sorted(grouped.items())]


def build_group_summary(group_value: str, items: list[ProfileReviewRow], group_kind: str) -> TransitionGroupSensitivitySummary:
    return _build_summary(group_value, items, group_kind)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def count_sensitivity(rows: list[ProfileReviewRow], sensitivity_class: str) -> int:
    return sum(1 for row in rows if row.transition_sensitivity_class == sensitivity_class)


def _build_summary(
    group_value: str,
    items: list[ProfileReviewRow],
    group_kind: str,
) -> TransitionGroupSensitivitySummary:
    high = count_sensitivity(items, "HIGH_TRANSITION_SCENARIO_SENSITIVITY")
    moderate = count_sensitivity(items, "MODERATE_TRANSITION_SCENARIO_SENSITIVITY")
    low = count_sensitivity(items, "LOW_TRANSITION_SCENARIO_SENSITIVITY")
    focus = sum(1 for item in items if item.focus_transition_flag == "YES")
    near = sum(1 for item in items if item.near_aggregation_candidate_flag == "YES")
    diagnostic = (
        transition_family_diagnostic(high, near, len(items))
        if group_kind == "family"
        else "Transition profiles connected to this state require further scenario-sensitive review"
    )
    return TransitionGroupSensitivitySummary(
        group_value=group_value,
        profile_count=len(items),
        high_sensitivity_profile_count=high,
        moderate_sensitivity_profile_count=moderate,
        low_sensitivity_profile_count=low,
        focus_profile_count=focus,
        near_aggregation_candidate_count=near,
        average_forward_range_cv=mean([item.forward_range_cv for item in items]),
        average_outcome_magnitude_cv=mean([item.outcome_magnitude_cv for item in items]),
        average_direction_alignment_dispersion=mean([item.direction_alignment_dispersion for item in items]),
        most_common_dispersion_driver=most_common([item.dispersion_driver_class for item in items], "LOW_DISPERSION"),
        sensitivity_diagnostic=diagnostic,
        recommended_follow_up=group_follow_up(high, near, len(items)),
    )
