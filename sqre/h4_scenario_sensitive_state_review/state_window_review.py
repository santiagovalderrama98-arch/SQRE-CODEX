"""State and forward-window sensitivity summaries."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_scenario_sensitive_state_review.classification import most_common
from sqre.h4_scenario_sensitive_state_review.findings import state_sensitivity_diagnostic, window_sensitivity_diagnostic
from sqre.h4_scenario_sensitive_state_review.models import ProfileReviewRow, StateSensitivitySummary, WindowSensitivitySummary


def build_state_sensitivity_summary(rows: list[ProfileReviewRow]) -> list[StateSensitivitySummary]:
    grouped: dict[str, list[ProfileReviewRow]] = defaultdict(list)
    for row in rows:
        grouped[row.condition_label].append(row)

    summaries: list[StateSensitivitySummary] = []
    for condition_label, items in sorted(grouped.items()):
        high = _count(items, "HIGH_SCENARIO_SENSITIVITY")
        moderate = _count(items, "MODERATE_SCENARIO_SENSITIVITY")
        low = _count(items, "LOW_SCENARIO_SENSITIVITY")
        near = sum(1 for item in items if item.near_aggregation_candidate_flag == "YES")
        summaries.append(
            StateSensitivitySummary(
                condition_label=condition_label,
                profile_count=len(items),
                high_sensitivity_profile_count=high,
                moderate_sensitivity_profile_count=moderate,
                low_sensitivity_profile_count=low,
                near_aggregation_candidate_count=near,
                average_forward_range_cv=mean([item.forward_range_cv for item in items]),
                average_outcome_magnitude_cv=mean([item.outcome_magnitude_cv for item in items]),
                average_direction_alignment_dispersion=mean([item.direction_alignment_dispersion for item in items]),
                most_common_dispersion_driver=most_common([item.dispersion_driver_class for item in items], "LOW_DISPERSION"),
                state_sensitivity_diagnostic=state_sensitivity_diagnostic(high, near, len(items)),
                recommended_follow_up=_follow_up(high, near, len(items)),
            )
        )
    return summaries


def build_window_sensitivity_summary(rows: list[ProfileReviewRow]) -> list[WindowSensitivitySummary]:
    grouped: dict[int, list[ProfileReviewRow]] = defaultdict(list)
    for row in rows:
        grouped[row.forward_window].append(row)

    summaries: list[WindowSensitivitySummary] = []
    for forward_window, items in sorted(grouped.items()):
        high = _count(items, "HIGH_SCENARIO_SENSITIVITY")
        moderate = _count(items, "MODERATE_SCENARIO_SENSITIVITY")
        low = _count(items, "LOW_SCENARIO_SENSITIVITY")
        near = sum(1 for item in items if item.near_aggregation_candidate_flag == "YES")
        summaries.append(
            WindowSensitivitySummary(
                forward_window=forward_window,
                profile_count=len(items),
                high_sensitivity_profile_count=high,
                moderate_sensitivity_profile_count=moderate,
                low_sensitivity_profile_count=low,
                near_aggregation_candidate_count=near,
                average_forward_range_cv=mean([item.forward_range_cv for item in items]),
                average_outcome_magnitude_cv=mean([item.outcome_magnitude_cv for item in items]),
                average_direction_alignment_dispersion=mean([item.direction_alignment_dispersion for item in items]),
                most_common_dispersion_driver=most_common([item.dispersion_driver_class for item in items], "LOW_DISPERSION"),
                window_sensitivity_diagnostic=window_sensitivity_diagnostic(high, near, len(items)),
                recommended_follow_up=_follow_up(high, near, len(items)),
            )
        )
    return summaries


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _count(rows: list[ProfileReviewRow], sensitivity_class: str) -> int:
    return sum(1 for row in rows if row.scenario_sensitivity_class == sensitivity_class)


def _follow_up(high_count: int, near_count: int, total_count: int) -> str:
    if near_count > 0:
        return "Review near-candidate profiles separately."
    if total_count and high_count > total_count / 2:
        return "Continue scenario-sensitive interpretation."
    return "Continue descriptive review."
