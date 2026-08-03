"""Map timestamped H4 rows to aggregate Phase 7.5.13 contexts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_context_table_generation.loader import (
    FORWARD_WINDOW_ALIASES,
    SOURCE_STATE_ALIASES,
    TARGET_STATE_ALIASES,
    TRANSITION_ALIASES,
    normalized_key,
    read_optional_csv,
    row_text,
)
from sqre.h4_timestamped_context_table_generation.models import TimestampedContextRow


CONTEXT_ID_ALIASES = ["Context_ID", "Aggregate_Context_ID", "context_id"]


def map_aggregate_contexts(rows: list[TimestampedContextRow], h4_combined_context_dir: Path) -> list[TimestampedContextRow]:
    aggregate = read_optional_csv(h4_combined_context_dir / "h4_transition_state_context_inventory.csv")
    if aggregate.empty:
        return [_with_no_match(row, "Aggregate context inventory is missing or empty.") for row in rows]

    mapped: list[TimestampedContextRow] = []
    for row in rows:
        match = _match_transition_window(row, aggregate)
        if match is not None:
            mapped.append(_matched(row, match, "TRANSITION_LABEL_FORWARD_WINDOW_MATCH", "HIGH_CONFIDENCE_CONTEXT_MATCH"))
            continue
        match = _match_state_pair_window(row, aggregate)
        if match is not None:
            mapped.append(_matched(row, match, "STATE_PAIR_FORWARD_WINDOW_MATCH", "MODERATE_CONFIDENCE_CONTEXT_MATCH"))
            continue
        match = _match_state_only_window(row, aggregate)
        if match is not None:
            mapped.append(_matched(row, match, "STATE_ONLY_FORWARD_WINDOW_MATCH", "LOW_CONFIDENCE_CONTEXT_MATCH"))
            continue
        mapped.append(_with_no_match(row, "No aggregate H4 context matched this timestamped row."))
    return mapped


def _match_transition_window(row: TimestampedContextRow, aggregate: pd.DataFrame) -> pd.Series | None:
    if not row.h4_transition_label or not row.h4_forward_window:
        return None
    for _, candidate in aggregate.iterrows():
        if normalized_key(row_text(candidate, TRANSITION_ALIASES)) != normalized_key(row.h4_transition_label):
            continue
        if normalized_key(row_text(candidate, FORWARD_WINDOW_ALIASES)) == normalized_key(row.h4_forward_window):
            return candidate
    return None


def _match_state_pair_window(row: TimestampedContextRow, aggregate: pd.DataFrame) -> pd.Series | None:
    if not row.h4_source_state or not row.h4_target_state or not row.h4_forward_window:
        return None
    for _, candidate in aggregate.iterrows():
        if normalized_key(row_text(candidate, SOURCE_STATE_ALIASES)) != normalized_key(row.h4_source_state):
            continue
        if normalized_key(row_text(candidate, TARGET_STATE_ALIASES)) != normalized_key(row.h4_target_state):
            continue
        if normalized_key(row_text(candidate, FORWARD_WINDOW_ALIASES)) == normalized_key(row.h4_forward_window):
            return candidate
    return None


def _match_state_only_window(row: TimestampedContextRow, aggregate: pd.DataFrame) -> pd.Series | None:
    if not row.h4_target_state or not row.h4_forward_window:
        return None
    for _, candidate in aggregate.iterrows():
        state_matches = normalized_key(row_text(candidate, TARGET_STATE_ALIASES)) == normalized_key(row.h4_target_state)
        state_matches = state_matches or normalized_key(row_text(candidate, SOURCE_STATE_ALIASES)) == normalized_key(row.h4_target_state)
        if not state_matches:
            continue
        if normalized_key(row_text(candidate, FORWARD_WINDOW_ALIASES)) == normalized_key(row.h4_forward_window):
            return candidate
    return None


def _matched(row: TimestampedContextRow, match: pd.Series, method: str, confidence: str) -> TimestampedContextRow:
    context_id = row_text(match, CONTEXT_ID_ALIASES, "")
    return replace(
        row,
        aggregate_context_id=context_id,
        aggregate_context_match_method=method,
        aggregate_context_match_confidence=confidence,
        context_row_diagnostic="Timestamped H4 row matched to an aggregate H4 context.",
    )


def _with_no_match(row: TimestampedContextRow, diagnostic: str) -> TimestampedContextRow:
    return replace(
        row,
        aggregate_context_id="",
        aggregate_context_match_method="NO_AGGREGATE_CONTEXT_MATCH",
        aggregate_context_match_confidence="NO_CONTEXT_MATCH",
        context_row_diagnostic=diagnostic,
    )
