"""Outcome statistics for selected H4 transition profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.findings import (
    outcome_profile_diagnostic,
    outcome_profile_follow_up,
    stability_class,
)
from sqre.h4_transition_outcome_deep_dive.models import OutcomeStatisticsRow, ScenarioBreakdownRow


def build_outcome_statistics(
    breakdown_rows: list[ScenarioBreakdownRow],
    config: H4TransitionOutcomeDeepDiveConfig,
) -> list[OutcomeStatisticsRow]:
    grouped: dict[tuple[str, int, str], list[ScenarioBreakdownRow]] = defaultdict(list)
    for row in breakdown_rows:
        grouped[(row.condition_label, row.forward_window, row.profile_type)].append(row)
    return [_statistics_row(label, window, profile_type, rows, config) for (label, window, profile_type), rows in sorted(grouped.items())]


def coefficient_of_variation(dispersion: float, average: float) -> float:
    if average == 0:
        return 0.0
    return abs(dispersion / average)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _statistics_row(
    label: str,
    window: int,
    profile_type: str,
    rows: list[ScenarioBreakdownRow],
    config: H4TransitionOutcomeDeepDiveConfig,
) -> OutcomeStatisticsRow:
    close_returns = [row.average_forward_close_return_pips for row in rows]
    ranges = [row.average_forward_range_pips for row in rows]
    magnitudes = [row.average_outcome_magnitude_pips for row in rows]
    alignments = [row.direction_alignment_rate for row in rows]
    range_average = mean(ranges)
    magnitude_average = mean(magnitudes)
    range_dispersion = _dispersion(ranges)
    magnitude_dispersion = _dispersion(magnitudes)
    range_cv = coefficient_of_variation(range_dispersion, range_average)
    magnitude_cv = coefficient_of_variation(magnitude_dispersion, magnitude_average)
    stability = stability_class(range_cv, magnitude_cv, config)
    return OutcomeStatisticsRow(
        condition_label=label,
        source_state=rows[0].source_state,
        target_state=rows[0].target_state,
        transition_family=rows[0].transition_family,
        forward_window=window,
        profile_type=profile_type,
        scenario_count=len({row.scenario_id for row in rows}),
        total_sample_size=sum(row.sample_size for row in rows),
        average_sample_size_per_scenario=mean([row.sample_size for row in rows]),
        average_forward_close_return_pips=mean(close_returns),
        min_forward_close_return_pips=min(close_returns) if close_returns else 0.0,
        max_forward_close_return_pips=max(close_returns) if close_returns else 0.0,
        forward_close_return_dispersion_pips=_dispersion(close_returns),
        average_forward_range_pips=range_average,
        min_forward_range_pips=min(ranges) if ranges else 0.0,
        max_forward_range_pips=max(ranges) if ranges else 0.0,
        forward_range_dispersion_pips=range_dispersion,
        forward_range_cv=range_cv,
        average_outcome_magnitude_pips=magnitude_average,
        min_outcome_magnitude_pips=min(magnitudes) if magnitudes else 0.0,
        max_outcome_magnitude_pips=max(magnitudes) if magnitudes else 0.0,
        outcome_magnitude_dispersion_pips=magnitude_dispersion,
        outcome_magnitude_cv=magnitude_cv,
        average_direction_alignment_rate=mean(alignments),
        min_direction_alignment_rate=min(alignments) if alignments else 0.0,
        max_direction_alignment_rate=max(alignments) if alignments else 0.0,
        direction_alignment_dispersion=_dispersion(alignments),
        outcome_profile_stability_class=stability,
        outcome_profile_diagnostic=outcome_profile_diagnostic(profile_type, stability),
        recommended_follow_up=outcome_profile_follow_up(stability, profile_type),
    )


def _dispersion(values: list[float]) -> float:
    if not values:
        return 0.0
    return max(values) - min(values)
