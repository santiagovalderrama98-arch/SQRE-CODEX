"""Fallback matching engine for research query requests."""

from __future__ import annotations

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_reference_store_usage_review.reference_query_builder import (
    find_column,
    int_value,
    row_value,
    same_text,
    text_value,
)


TRACE_COLUMNS = [
    "Research_Query_ID",
    "Fallback_Attempt_Order",
    "Attempted_Match_Level",
    "Attempted_H4_Transition_Label",
    "Attempted_D1_Market_State",
    "Attempted_D1_Regime_Label",
    "Attempted_Forward_Horizon_H4_Candles",
    "Candidate_Reference_Count",
    "Selected_Result_Count",
    "Fallback_Attempt_Status",
    "Fallback_Diagnostic",
]
MATCH_LEVELS = [
    "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH",
    "D1_REGIME_CONTEXT_QUERY_MATCH",
    "D1_MARKET_STATE_CONTEXT_QUERY_MATCH",
    "H4_TRANSITION_ONLY_QUERY_MATCH",
    "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH",
]


def find_research_reference_matches(
    query: pd.Series,
    reference_store: pd.DataFrame,
    config: ResearchQueryInterfaceDesignConfig,
) -> tuple[pd.DataFrame, list[dict[str, object]], str]:
    if query.get("Query_Validation_Status") == "INPUT_MISSING":
        return pd.DataFrame(), [_trace(query, 1, "INPUT_MISSING", 0, 0, "INPUT_MISSING", "Query inputs are missing.")], "INPUT_MISSING"
    if query.get("Query_Validation_Status") == "INVALID_RESEARCH_QUERY" or reference_store.empty:
        diagnostic = "Query is invalid." if reference_store.empty is False else "Research reference store has no rows."
        return (
            pd.DataFrame(),
            [_trace(query, 1, "NO_RESEARCH_REFERENCE_QUERY_MATCH", 0, 0, "NO_MATCH_FOUND", diagnostic)],
            "NO_RESEARCH_REFERENCE_QUERY_MATCH",
        )

    trace_rows: list[dict[str, object]] = []
    for attempt_order, match_level in enumerate(MATCH_LEVELS, start=1):
        if _should_skip(query, match_level):
            trace_rows.append(
                _trace(
                    query,
                    attempt_order,
                    match_level,
                    0,
                    0,
                    "SKIPPED_INSUFFICIENT_QUERY_FIELDS",
                    "Required query fields for this fallback level are missing.",
                )
            )
            continue
        matches = _filter(reference_store, query, match_level)
        selected = min(len(matches), config.maximum_results_per_query)
        status = "MATCH_FOUND" if not matches.empty else "NO_MATCH_FOUND"
        diagnostic = f"{len(matches)} candidate references found." if not matches.empty else "No candidate references found."
        trace_rows.append(_trace(query, attempt_order, match_level, len(matches), selected, status, diagnostic))
        if not matches.empty:
            return matches, trace_rows, match_level

    trace_rows.append(
        _trace(
            query,
            len(trace_rows) + 1,
            "NO_RESEARCH_REFERENCE_QUERY_MATCH",
            0,
            0,
            "NO_MATCH_FOUND",
            "No descriptive research reference matched this query.",
        )
    )
    return pd.DataFrame(), trace_rows, "NO_RESEARCH_REFERENCE_QUERY_MATCH"


def _should_skip(query: pd.Series, match_level: str) -> bool:
    horizon = int_value(query.get("Requested_Forward_Horizon_H4_Candles", 0))
    if _blank(query.get("H4_Transition_Label", "")):
        return True
    if match_level != "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH" and horizon <= 0:
        return True
    if match_level == "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH":
        return _blank(query.get("D1_Market_State", "")) or _blank(query.get("D1_Regime_Label", ""))
    if match_level == "D1_REGIME_CONTEXT_QUERY_MATCH":
        return _blank(query.get("D1_Regime_Label", ""))
    if match_level == "D1_MARKET_STATE_CONTEXT_QUERY_MATCH":
        return _blank(query.get("D1_Market_State", ""))
    return False


def _filter(frame: pd.DataFrame, query: pd.Series, match_level: str) -> pd.DataFrame:
    matches = _match_column(frame, "H4_Transition_Label", query.get("H4_Transition_Label", ""))
    if match_level != "BROADER_H4_TRANSITION_ANY_HORIZON_QUERY_MATCH":
        matches = _match_column(matches, "Forward_Horizon_H4_Candles", query.get("Requested_Forward_Horizon_H4_Candles", 0))
    if match_level == "EXACT_D1_STATE_REGIME_CONTEXT_QUERY_MATCH":
        matches = _match_column(matches, "D1_Market_State", query.get("D1_Market_State", ""))
        matches = _match_column(matches, "D1_Regime_Label", query.get("D1_Regime_Label", ""))
    elif match_level == "D1_REGIME_CONTEXT_QUERY_MATCH":
        matches = _match_column(matches, "D1_Regime_Label", query.get("D1_Regime_Label", ""))
    elif match_level == "D1_MARKET_STATE_CONTEXT_QUERY_MATCH":
        matches = _match_column(matches, "D1_Market_State", query.get("D1_Market_State", ""))
    return matches


def _match_column(frame: pd.DataFrame, column_name: str, expected: object) -> pd.DataFrame:
    column = find_column(frame, [column_name])
    if column is None:
        return pd.DataFrame(columns=frame.columns)
    return frame[frame[column].map(lambda item: same_text(item, expected))]


def _blank(value: object) -> bool:
    text = text_value(value)
    return not text or text.upper() == "INPUT_MISSING"


def _trace(
    query: pd.Series,
    attempt_order: int,
    match_level: str,
    candidate_count: int,
    selected_count: int,
    status: str,
    diagnostic: str,
) -> dict[str, object]:
    return {
        "Research_Query_ID": text_value(query.get("Research_Query_ID", "")),
        "Fallback_Attempt_Order": attempt_order,
        "Attempted_Match_Level": match_level,
        "Attempted_H4_Transition_Label": text_value(query.get("H4_Transition_Label", "")),
        "Attempted_D1_Market_State": text_value(query.get("D1_Market_State", "")),
        "Attempted_D1_Regime_Label": text_value(query.get("D1_Regime_Label", "")),
        "Attempted_Forward_Horizon_H4_Candles": int_value(
            row_value(query, ["Requested_Forward_Horizon_H4_Candles", "Forward_Horizon_H4_Candles"], 0)
        ),
        "Candidate_Reference_Count": candidate_count,
        "Selected_Result_Count": selected_count,
        "Fallback_Attempt_Status": status,
        "Fallback_Diagnostic": diagnostic,
    }

