"""Descriptive behavior summary for snapshot reference results."""

from __future__ import annotations

import pandas as pd


SNAPSHOT_BEHAVIOR_SUMMARY_COLUMNS = [
    "Snapshot_ID",
    "Snapshot_Query_Count",
    "Snapshot_Result_Count",
    "Matched_Horizon_Count",
    "Primary_Matched_Horizon",
    "Primary_Match_Level",
    "Primary_Evidence_Class",
    "High_Evidence_Result_Count",
    "Moderate_Evidence_Result_Count",
    "Low_Evidence_Result_Count",
    "No_Usable_Result_Count",
    "Core_Evidence_Result_Count",
    "Supporting_Evidence_Result_Count",
    "Observed_Direction_Class_Count",
    "Dominant_Observed_Direction_Count",
    "Behavior_Summary_Diagnostic",
]


def build_snapshot_behavior_summary(snapshot_queries: pd.DataFrame, snapshot_results: pd.DataFrame) -> pd.DataFrame:
    if snapshot_queries.empty:
        return pd.DataFrame(columns=SNAPSHOT_BEHAVIOR_SUMMARY_COLUMNS)
    snapshot_id = str(snapshot_queries.iloc[0].get("Snapshot_ID", ""))
    matched = snapshot_results[snapshot_results["Matched_Research_Reference_ID"].astype(str) != ""] if not snapshot_results.empty else pd.DataFrame()
    rows = [
        {
            "Snapshot_ID": snapshot_id,
            "Snapshot_Query_Count": len(snapshot_queries),
            "Snapshot_Result_Count": len(snapshot_results),
            "Matched_Horizon_Count": matched["Matched_Forward_Horizon_H4_Candles"].nunique() if not matched.empty else 0,
            "Primary_Matched_Horizon": _mode(matched, "Matched_Forward_Horizon_H4_Candles"),
            "Primary_Match_Level": _mode(snapshot_results, "Snapshot_Query_Match_Level"),
            "Primary_Evidence_Class": _mode(snapshot_results, "Snapshot_Evidence_Class"),
            "High_Evidence_Result_Count": _count(snapshot_results, "Snapshot_Research_Result_Class", "HIGH_EVIDENCE_SNAPSHOT_REFERENCE"),
            "Moderate_Evidence_Result_Count": _count(
                snapshot_results, "Snapshot_Research_Result_Class", "MODERATE_EVIDENCE_SNAPSHOT_REFERENCE"
            ),
            "Low_Evidence_Result_Count": _count(snapshot_results, "Snapshot_Research_Result_Class", "LOW_EVIDENCE_SNAPSHOT_REFERENCE"),
            "No_Usable_Result_Count": _count(snapshot_results, "Snapshot_Research_Result_Class", "NO_USABLE_SNAPSHOT_REFERENCE"),
            "Core_Evidence_Result_Count": _count(snapshot_results, "Snapshot_Evidence_Class", "CORE_SNAPSHOT_REFERENCE_EVIDENCE"),
            "Supporting_Evidence_Result_Count": _count(
                snapshot_results, "Snapshot_Evidence_Class", "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE"
            ),
            "Observed_Direction_Class_Count": matched["Matched_Directional_Behavior_Class"].replace("", pd.NA).dropna().nunique()
            if not matched.empty
            else 0,
            "Dominant_Observed_Direction_Count": _mode_count(matched, "Matched_Dominant_Observed_Direction"),
            "Behavior_Summary_Diagnostic": _diagnostic(len(snapshot_queries), len(matched)),
        }
    ]
    return pd.DataFrame(rows, columns=SNAPSHOT_BEHAVIOR_SUMMARY_COLUMNS)


def _count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column] == value).sum())


def _mode(frame: pd.DataFrame, column: str) -> str:
    if frame.empty or column not in frame.columns:
        return ""
    values = frame[column].replace("", pd.NA).dropna()
    if values.empty:
        return ""
    return str(values.value_counts().idxmax())


def _mode_count(frame: pd.DataFrame, column: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    values = frame[column].replace("", pd.NA).dropna()
    if values.empty:
        return 0
    return int(values.value_counts().iloc[0])


def _diagnostic(query_count: int, matched_count: int) -> str:
    if matched_count == 0:
        return "No descriptive historical references were matched for the snapshot."
    return f"{matched_count} descriptive historical references were matched across {query_count} snapshot queries."
