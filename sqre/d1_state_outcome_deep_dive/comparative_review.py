"""Descriptive regime comparison matrix for D1 state profiles."""

from __future__ import annotations

from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.findings import regime_comparison_diagnostic, regime_deviation_class
from sqre.d1_state_outcome_deep_dive.models import OutcomeStatisticsRow, RegimeBreakdownRow, RegimeComparisonRow


def build_regime_comparison_matrix(
    breakdown_rows: list[RegimeBreakdownRow],
    statistics_rows: list[OutcomeStatisticsRow],
    config: D1StateOutcomeDeepDiveConfig,
) -> list[RegimeComparisonRow]:
    stats_by_key = {
        (row.condition_label, row.forward_window, row.profile_type): row
        for row in statistics_rows
    }
    comparison_rows: list[RegimeComparisonRow] = []
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
        deviation_class = regime_deviation_class(sum(normalized) / len(normalized), config)
        comparison_rows.append(
            RegimeComparisonRow(
                condition_label=row.condition_label,
                forward_window=row.forward_window,
                regime_id=row.regime_id,
                regime_label=row.regime_label,
                scenario_id=row.scenario_id,
                sample_size=row.sample_size,
                forward_close_return_vs_profile_avg=close_diff,
                forward_range_vs_profile_avg=range_diff,
                outcome_magnitude_vs_profile_avg=magnitude_diff,
                direction_alignment_vs_profile_avg=alignment_diff,
                regime_deviation_class=deviation_class,
                regime_comparison_diagnostic=regime_comparison_diagnostic(deviation_class),
            )
        )
    return comparison_rows


def _normalized_abs(value: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return abs(value / denominator)
