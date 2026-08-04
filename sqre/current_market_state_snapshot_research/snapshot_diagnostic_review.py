"""Diagnostic review rows for snapshot workflow."""

from __future__ import annotations

import pandas as pd


SNAPSHOT_DIAGNOSTIC_REVIEW_COLUMNS = [
    "Diagnostic_Category",
    "Diagnostic_Status",
    "Diagnostic_Count",
    "Diagnostic_Message",
]


def build_snapshot_diagnostic_review(
    snapshot_context: pd.DataFrame,
    snapshot_queries: pd.DataFrame,
    snapshot_results: pd.DataFrame,
    fallback_trace: pd.DataFrame,
) -> pd.DataFrame:
    validation_status = _first(snapshot_context, "Snapshot_Validation_Status", "INPUT_MISSING")
    query_without = _query_without_result_count(snapshot_queries, snapshot_results)
    rows = [
        {
            "Diagnostic_Category": "SNAPSHOT_CONTEXT",
            "Diagnostic_Status": validation_status,
            "Diagnostic_Count": len(snapshot_context),
            "Diagnostic_Message": _first(snapshot_context, "Snapshot_Diagnostic", "No snapshot context was built."),
        },
        {
            "Diagnostic_Category": "SNAPSHOT_QUERY_COVERAGE",
            "Diagnostic_Status": "SNAPSHOT_QUERIES_WITHOUT_RESULTS" if query_without else "SNAPSHOT_QUERIES_WITH_RESULTS",
            "Diagnostic_Count": query_without,
            "Diagnostic_Message": f"{query_without} snapshot queries had no descriptive reference result.",
        },
        {
            "Diagnostic_Category": "FALLBACK_TRACE",
            "Diagnostic_Status": "TRACE_AVAILABLE" if not fallback_trace.empty else "TRACE_MISSING",
            "Diagnostic_Count": len(fallback_trace),
            "Diagnostic_Message": "Fallback trace records describe each snapshot lookup attempt.",
        },
    ]
    return pd.DataFrame(rows, columns=SNAPSHOT_DIAGNOSTIC_REVIEW_COLUMNS)


def _first(frame: pd.DataFrame, column: str, default: str) -> str:
    if frame.empty or column not in frame.columns:
        return default
    return str(frame.iloc[0].get(column, default))


def _query_without_result_count(snapshot_queries: pd.DataFrame, snapshot_results: pd.DataFrame) -> int:
    if snapshot_queries.empty:
        return 0
    if snapshot_results.empty:
        return len(snapshot_queries)
    matched = set(
        snapshot_results.loc[
            snapshot_results["Matched_Research_Reference_ID"].astype(str) != "",
            "Snapshot_Query_ID",
        ]
    )
    return len([item for item in snapshot_queries["Snapshot_Query_ID"] if item not in matched])
