"""Scenario comparison matrix for H4 transition profiles."""

from __future__ import annotations

from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.findings import scenario_comparison_diagnostic, scenario_deviation_class
from sqre.h4_transition_outcome_deep_dive.models import OutcomeStatisticsRow, ScenarioBreakdownRow, ScenarioComparisonRow


def build_scenario_comparison_matrix(
    breakdown_rows: list[ScenarioBreakdownRow],
    statistics_rows: list[OutcomeStatisticsRow],
    config: H4TransitionOutcomeDeepDiveConfig,
) -> list[ScenarioComparisonRow]:
    stats_by_key = {
        (row.condition_label, row.forward_window, row.profile_type): row
        for row in statistics_rows
    }
    comparison_rows: list[ScenarioComparisonRow] = []
    for row in breakdown_rows:
        stats = stats_by_key[(row.condition_label, row.forward_window, row.profile_type)]
        close_diff = row.average_forward_close_return_pips - stats.average_forward_close_return_pips
        range_diff = row.average_forward_range_pips - stats.average_forward_range_pips
        magnitude_diff = row.average_outcome_magnitude_pips - stats.average_outcome_magnitude_pips
        alignment_diff = row.direction_alignment_rate - stats.average_direction_alignment_rate
        normalized = [
            _normalized_abs(range_diff, stats.average_forward_range_pips),
            _normalized_abs(magnitude_diff, stats.average_outcome_magnitude_pips),
            _normalized_abs(alignment_diff, stats.average_direction_alignment_rate),
        ]
        deviation_class = scenario_deviation_class(sum(normalized) / len(normalized), config)
        comparison_rows.append(
            ScenarioComparisonRow(
                condition_label=row.condition_label,
                source_state=row.source_state,
                target_state=row.target_state,
                transition_family=row.transition_family,
                forward_window=row.forward_window,
                scenario_id=row.scenario_id,
                sample_size=row.sample_size,
                forward_close_return_vs_profile_avg=close_diff,
                forward_range_vs_profile_avg=range_diff,
                outcome_magnitude_vs_profile_avg=magnitude_diff,
                direction_alignment_vs_profile_avg=alignment_diff,
                scenario_deviation_class=deviation_class,
                scenario_comparison_diagnostic=scenario_comparison_diagnostic(deviation_class),
            )
        )
    return comparison_rows


def _normalized_abs(value: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return abs(value / denominator)
