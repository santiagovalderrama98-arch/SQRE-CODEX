"""Aggregate query result and evidence quality."""

from __future__ import annotations

import pandas as pd


RESULT_QUALITY_COLUMNS = [
    "Research_Query_Result_Quality_Class",
    "Query_Result_Count",
    "Unique_Query_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Result_Quality_Diagnostic",
]
EVIDENCE_QUALITY_COLUMNS = [
    "Research_Query_Evidence_Class",
    "Query_Result_Count",
    "Unique_Query_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Evidence_Quality_Diagnostic",
]


def build_query_result_quality_review(query_results: pd.DataFrame) -> pd.DataFrame:
    return _group_quality(query_results, "Research_Query_Result_Quality_Class", RESULT_QUALITY_COLUMNS, "Result_Quality_Diagnostic")


def build_query_evidence_quality_review(query_results: pd.DataFrame) -> pd.DataFrame:
    return _group_quality(query_results, "Research_Query_Evidence_Class", EVIDENCE_QUALITY_COLUMNS, "Evidence_Quality_Diagnostic")


def _group_quality(frame: pd.DataFrame, group_column: str, columns: list[str], diagnostic_column: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=columns)
    rows = []
    for quality_class, group in frame.groupby(group_column, dropna=False):
        rows.append(
            {
                group_column: quality_class,
                "Query_Result_Count": len(group),
                "Unique_Query_Count": group["Research_Query_ID"].nunique(),
                "Core_Reference_Count": int((group["Matched_Reference_Tier"] == "CORE_REFERENCE").sum()),
                "Supporting_Reference_Count": int((group["Matched_Reference_Tier"] == "SUPPORTING_REFERENCE").sum()),
                "Average_Outcome_Sample_Size": round(float(group["Matched_Outcome_Sample_Size"].mean()), 4),
                "Average_Outcome_Dispersion_Pips": round(float(group["Matched_Outcome_Dispersion_Pips"].mean()), 4),
                diagnostic_column: f"{len(group)} descriptive query results classified as {quality_class}.",
            }
        )
    return pd.DataFrame(rows, columns=columns)

