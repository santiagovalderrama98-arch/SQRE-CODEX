"""Source and target state sensitivity summaries for transition profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_transition_scenario_sensitive_review.findings import group_follow_up, state_sensitivity_diagnostic
from sqre.h4_transition_scenario_sensitive_review.models import ProfileReviewRow, TransitionGroupSensitivitySummary
from sqre.h4_transition_scenario_sensitive_review.profile_selector import most_common
from sqre.h4_transition_scenario_sensitive_review.transition_family_review import count_sensitivity, mean


def build_source_state_sensitivity_summary(rows: list[ProfileReviewRow]) -> list[TransitionGroupSensitivitySummary]:
    return _build_state_summary(rows, "source")


def build_target_state_sensitivity_summary(rows: list[ProfileReviewRow]) -> list[TransitionGroupSensitivitySummary]:
    return _build_state_summary(rows, "target")


def _build_state_summary(rows: list[ProfileReviewRow], state_kind: str) -> list[TransitionGroupSensitivitySummary]:
    grouped: dict[str, list[ProfileReviewRow]] = defaultdict(list)
    for row in rows:
        grouped[row.source_state if state_kind == "source" else row.target_state].append(row)

    summaries: list[TransitionGroupSensitivitySummary] = []
    for state, items in sorted(grouped.items()):
        high = count_sensitivity(items, "HIGH_TRANSITION_SCENARIO_SENSITIVITY")
        moderate = count_sensitivity(items, "MODERATE_TRANSITION_SCENARIO_SENSITIVITY")
        low = count_sensitivity(items, "LOW_TRANSITION_SCENARIO_SENSITIVITY")
        focus = sum(1 for item in items if item.focus_transition_flag == "YES")
        near = sum(1 for item in items if item.near_aggregation_candidate_flag == "YES")
        summaries.append(
            TransitionGroupSensitivitySummary(
                group_value=state,
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
                sensitivity_diagnostic=state_sensitivity_diagnostic(high, near, len(items)),
                recommended_follow_up=group_follow_up(high, near, len(items)),
            )
        )
    return summaries
