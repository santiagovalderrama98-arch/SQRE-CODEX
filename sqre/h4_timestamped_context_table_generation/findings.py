"""Findings and readiness classification for H4 timestamped context table generation."""

from __future__ import annotations

from collections import Counter

from sqre.h4_timestamped_context_table_generation.coverage_review import dominant_coverage_class
from sqre.h4_timestamped_context_table_generation.models import (
    CoverageReviewRow,
    H4TimestampedContextGenerationSummary,
    SourceInventoryRow,
    TimestampedContextRow,
)


def build_summary(
    source_inventory: list[SourceInventoryRow],
    coverage_review: list[CoverageReviewRow],
    context_rows: list[TimestampedContextRow],
    symbol: str,
    timeframe: str,
) -> H4TimestampedContextGenerationSummary:
    matched = sum(1 for row in context_rows if row.aggregate_context_id)
    complete = sum(1 for row in context_rows if row.h4_temporal_key_class != "TEMPORAL_KEY_INCOMPLETE")
    coverage_counts = Counter(row.coverage_class for row in coverage_review)
    dominant = dominant_coverage_class(coverage_review)
    readiness = _readiness_flag(dominant, len(context_rows), complete, len(coverage_review))
    return H4TimestampedContextGenerationSummary(
        symbol=symbol,
        timeframe=timeframe,
        scenario_count=len(coverage_review),
        timestamped_source_count=sum(
            1
            for row in source_inventory
            if row.load_status == "LOADED" and row.timestamp_columns and "TIMESTAMPED" in row.source_type
        ),
        timestamped_context_row_count=len(context_rows),
        aggregate_context_matched_row_count=matched,
        aggregate_context_unmatched_row_count=len(context_rows) - matched,
        temporal_key_complete_row_count=complete,
        temporal_key_incomplete_row_count=len(context_rows) - complete,
        full_coverage_scenario_count=coverage_counts.get("FULL_TEMPORAL_CONTEXT_COVERAGE", 0),
        partial_coverage_scenario_count=coverage_counts.get("PARTIAL_TEMPORAL_CONTEXT_COVERAGE", 0),
        low_coverage_scenario_count=coverage_counts.get("LOW_TEMPORAL_CONTEXT_COVERAGE", 0),
        missing_coverage_scenario_count=coverage_counts.get("NO_TEMPORAL_CONTEXT_COVERAGE", 0),
        dominant_coverage_class=dominant,
        h4_timestamped_context_readiness_flag=readiness,
        h4_timestamped_context_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_follow_up(readiness),
    )


def descriptive_findings(summary: H4TimestampedContextGenerationSummary | None) -> list[str]:
    if summary is None:
        return ["- H4 timestamped context generation summary was not produced."]
    return [
        f"- Dominant coverage class: {summary.dominant_coverage_class}",
        f"- H4 timestamped context readiness flag: {summary.h4_timestamped_context_readiness_flag}",
        f"- Recommended follow-up: {summary.recommended_follow_up}",
        "- This review is generation-only and does not compare H4 with D1.",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4/D1 same-time contextual transition review",
        "D1 timestamped regime table generation",
        "H4/D1 interval overlap alignment table",
        "Research reference-store design",
        "Provider history coverage review",
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
        "Timestamped context generation depends on existing timestamped H4 state/transition outputs.",
        "Missing scenario identifiers may reduce coverage.",
        "Date key is not a completed D1 alignment.",
        "No operational decision is produced.",
    ]


def _readiness_flag(dominant: str, row_count: int, complete_count: int, scenario_count: int) -> str:
    if scenario_count == 0:
        return "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    if row_count == 0:
        return "NOT_READY_TIMESTAMPED_CONTEXT_MISSING"
    if complete_count < row_count:
        return "NOT_READY_TIMESTAMPED_CONTEXT_INCOMPLETE"
    if dominant == "FULL_TEMPORAL_CONTEXT_COVERAGE":
        return "READY_FOR_H4_D1_TEMPORAL_ALIGNMENT"
    if dominant == "PARTIAL_TEMPORAL_CONTEXT_COVERAGE":
        return "PARTIAL_READY_FOR_H4_D1_TEMPORAL_ALIGNMENT"
    return "NOT_READY_TIMESTAMPED_CONTEXT_INCOMPLETE"


def _diagnostic(readiness: str) -> str:
    mapping = {
        "READY_FOR_H4_D1_TEMPORAL_ALIGNMENT": "H4 timestamped context rows are available for later temporal alignment work.",
        "PARTIAL_READY_FOR_H4_D1_TEMPORAL_ALIGNMENT": "Some H4 scenarios have timestamped context rows, but coverage is partial.",
        "NOT_READY_TIMESTAMPED_CONTEXT_INCOMPLETE": "H4 timestamped context rows are incomplete.",
        "NOT_READY_TIMESTAMPED_CONTEXT_MISSING": "No timestamped H4 context rows were generated from available sources.",
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "Input completeness must be reviewed before timestamped context generation.",
    }
    return mapping.get(readiness, "H4 timestamped context readiness could not be classified.")


def _follow_up(readiness: str) -> str:
    if readiness == "READY_FOR_H4_D1_TEMPORAL_ALIGNMENT":
        return "PREPARE_H4_D1_TEMPORAL_ALIGNMENT_REVIEW"
    if readiness == "PARTIAL_READY_FOR_H4_D1_TEMPORAL_ALIGNMENT":
        return "EXPAND_TIMESTAMPED_H4_CONTEXT_COVERAGE"
    if readiness == "INPUT_COMPLETENESS_REVIEW_REQUIRED":
        return "REVIEW_VALIDATION_OUTPUT_DIRECTORY_STRUCTURE"
    return "GENERATE_STATE_TRANSITION_OUTPUTS_WITH_TIMESTAMPS"
