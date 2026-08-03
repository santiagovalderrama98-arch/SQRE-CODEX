"""Findings and readiness classification for H4 timestamped state/transition outputs."""

from __future__ import annotations

from collections import Counter

from sqre.h4_timestamped_state_transition_outputs.models import (
    CoverageReviewRow,
    H4TimestampedStateTransitionSummary,
    RegenerationResult,
    SourceInventoryRow,
    TimestampedMarketStateRow,
    TimestampedStateTransitionRow,
)
from sqre.h4_timestamped_state_transition_outputs.output_coverage_review import dominant_coverage_class


def build_summary(
    source_inventory: list[SourceInventoryRow],
    coverage_review: list[CoverageReviewRow],
    state_rows: list[TimestampedMarketStateRow],
    transition_rows: list[TimestampedStateTransitionRow],
    regeneration_results: list[RegenerationResult],
    symbol: str,
    timeframe: str,
) -> H4TimestampedStateTransitionSummary:
    coverage_counts = Counter(row.coverage_class for row in coverage_review)
    dominant = dominant_coverage_class(coverage_review)
    readiness = _readiness_flag(dominant, len(state_rows), len(transition_rows), len(coverage_review))
    return H4TimestampedStateTransitionSummary(
        symbol=symbol,
        timeframe=timeframe,
        scenario_count=len(coverage_review),
        source_inventory_row_count=len(source_inventory),
        timestamped_state_row_count=len(state_rows),
        timestamped_transition_row_count=len(transition_rows),
        scenario_with_full_timestamped_output_count=coverage_counts.get("FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE", 0),
        scenario_with_partial_timestamped_output_count=coverage_counts.get(
            "PARTIAL_TIMESTAMPED_STATE_TRANSITION_COVERAGE", 0
        ),
        scenario_with_missing_timestamped_output_count=coverage_counts.get("NO_TIMESTAMPED_STATE_TRANSITION_COVERAGE", 0),
        regenerated_scenario_count=sum(
            1 for row in regeneration_results if row.status == "REGENERATED_TIMESTAMPED_OUTPUTS_AVAILABLE"
        ),
        regeneration_failed_scenario_count=sum(1 for row in regeneration_results if row.status.endswith("MISSING")),
        dominant_output_coverage_class=dominant,
        h4_timestamped_state_transition_readiness_flag=readiness,
        h4_timestamped_state_transition_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_follow_up(readiness),
    )


def descriptive_findings(summary: H4TimestampedStateTransitionSummary | None) -> list[str]:
    if summary is None:
        return ["- H4 timestamped state/transition summary was not produced."]
    return [
        f"- Dominant output coverage class: {summary.dominant_output_coverage_class}",
        f"- H4 timestamped state transition readiness flag: {summary.h4_timestamped_state_transition_readiness_flag}",
        f"- Recommended follow-up: {summary.recommended_follow_up}",
        "- This review is generation-only and does not compare H4 with D1.",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4 timestamped context table generation retry",
        "D1 timestamped regime/state table generation",
        "H4/D1 interval overlap alignment table",
        "H4/D1 same-time contextual transition review",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No data was downloaded.",
        "No provider behavior was changed.",
        "No D1 alignment was produced.",
        "No same-time H4/D1 interpretation was produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local files currently present in workspace.",
        "Regeneration depends on available local raw OHLC files.",
        "Scenario identifiers may be missing from historical outputs.",
        "Generated outputs are research artifacts only.",
        "No operational decision is produced.",
    ]


def _readiness_flag(dominant: str, state_count: int, transition_count: int, scenario_count: int) -> str:
    if scenario_count == 0:
        return "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    if state_count == 0 and transition_count == 0:
        return "NOT_READY_STATE_TRANSITION_OUTPUTS_MISSING"
    if state_count > 0 and transition_count == 0:
        return "NOT_READY_TRANSITIONS_TIMESTAMPED_OUTPUT_MISSING"
    if state_count == 0 and transition_count > 0:
        return "NOT_READY_STATES_TIMESTAMPED_OUTPUT_MISSING"
    if dominant == "FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE":
        return "READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE"
    return "PARTIAL_READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE"


def _diagnostic(readiness: str) -> str:
    mapping = {
        "READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE": "H4 timestamped state and transition outputs are available.",
        "PARTIAL_READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE": "Some H4 timestamped state and transition outputs are available, but coverage is partial.",
        "NOT_READY_TRANSITIONS_TIMESTAMPED_OUTPUT_MISSING": "Timestamped state rows exist, but timestamped transition rows are missing.",
        "NOT_READY_STATES_TIMESTAMPED_OUTPUT_MISSING": "Timestamped transition rows exist, but timestamped state rows are missing.",
        "NOT_READY_STATE_TRANSITION_OUTPUTS_MISSING": "No timestamped H4 state/transition rows were generated from available sources.",
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "Input completeness must be reviewed before output generation.",
    }
    return mapping.get(readiness, "H4 timestamped state/transition readiness could not be classified.")


def _follow_up(readiness: str) -> str:
    if readiness in {"READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE", "PARTIAL_READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE"}:
        return "H4_TIMESTAMPED_CONTEXT_TABLE_GENERATION_RETRY"
    if readiness == "NOT_READY_TRANSITIONS_TIMESTAMPED_OUTPUT_MISSING":
        return "GENERATE_STATE_TRANSITIONS_WITH_TIMESTAMPS"
    if readiness == "NOT_READY_STATES_TIMESTAMPED_OUTPUT_MISSING":
        return "GENERATE_MARKET_STATES_WITH_TIMESTAMPS"
    if readiness == "INPUT_COMPLETENESS_REVIEW_REQUIRED":
        return "REVIEW_SCENARIO_INPUT_CONFIGURATION"
    return "GENERATE_STATE_TRANSITION_OUTPUTS_WITH_TIMESTAMPS"
