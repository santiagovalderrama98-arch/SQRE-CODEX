"""Coverage review for H4 timestamped context table generation."""

from __future__ import annotations

from collections import Counter

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.models import CoverageReviewRow, ScenarioInventoryRow, TimestampedContextRow


def build_coverage_review(
    scenarios: list[ScenarioInventoryRow],
    context_rows: list[TimestampedContextRow],
    config: H4TimestampedContextTableGenerationConfig,
) -> list[CoverageReviewRow]:
    by_scenario: dict[str, list[TimestampedContextRow]] = {}
    for row in context_rows:
        by_scenario.setdefault(row.scenario_id, []).append(row)
    coverage: list[CoverageReviewRow] = []
    for scenario in scenarios:
        rows = by_scenario.get(scenario.scenario_id, [])
        matched = sum(1 for row in rows if row.aggregate_context_id)
        complete = sum(1 for row in rows if row.h4_temporal_key_class != "TEMPORAL_KEY_INCOMPLETE")
        expected = scenario.transitions_generated or len(rows)
        ratio = len(rows) / expected if expected else 0.0
        coverage_class = _coverage_class(ratio, len(rows), config.minimum_scenario_coverage_ratio)
        coverage.append(
            CoverageReviewRow(
                scenario_id=scenario.scenario_id,
                symbol=scenario.symbol,
                timeframe=scenario.timeframe,
                period_start=scenario.period_start,
                period_end=scenario.period_end,
                expected_transition_count=expected,
                timestamped_context_row_count=len(rows),
                aggregate_context_matched_row_count=matched,
                aggregate_context_unmatched_row_count=len(rows) - matched,
                temporal_key_complete_row_count=complete,
                temporal_key_incomplete_row_count=len(rows) - complete,
                coverage_ratio=round(ratio, 4),
                coverage_class=coverage_class,
                coverage_diagnostic=_coverage_diagnostic(coverage_class),
            )
        )
    return coverage


def dominant_coverage_class(rows: list[CoverageReviewRow]) -> str:
    if not rows:
        return "NO_TEMPORAL_CONTEXT_COVERAGE"
    counts = Counter(row.coverage_class for row in rows)
    priority = [
        "FULL_TEMPORAL_CONTEXT_COVERAGE",
        "PARTIAL_TEMPORAL_CONTEXT_COVERAGE",
        "LOW_TEMPORAL_CONTEXT_COVERAGE",
        "NO_TEMPORAL_CONTEXT_COVERAGE",
    ]
    return max(priority, key=lambda item: (counts.get(item, 0), -priority.index(item)))


def _coverage_class(ratio: float, rows: int, minimum: float) -> str:
    if rows == 0:
        return "NO_TEMPORAL_CONTEXT_COVERAGE"
    if ratio >= minimum:
        return "FULL_TEMPORAL_CONTEXT_COVERAGE"
    if ratio >= 0.50:
        return "PARTIAL_TEMPORAL_CONTEXT_COVERAGE"
    return "LOW_TEMPORAL_CONTEXT_COVERAGE"


def _coverage_diagnostic(coverage_class: str) -> str:
    if coverage_class == "FULL_TEMPORAL_CONTEXT_COVERAGE":
        return "Scenario has sufficient timestamped H4 context coverage for a later temporal alignment review."
    if coverage_class == "PARTIAL_TEMPORAL_CONTEXT_COVERAGE":
        return "Scenario has partial timestamped H4 context coverage."
    if coverage_class == "LOW_TEMPORAL_CONTEXT_COVERAGE":
        return "Scenario has low timestamped H4 context coverage."
    return "Scenario has no timestamped H4 context rows."
