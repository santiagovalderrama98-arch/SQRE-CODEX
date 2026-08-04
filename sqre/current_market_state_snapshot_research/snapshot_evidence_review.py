"""Evidence review for snapshot reference results."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.reference_query_builder import float_value, int_value


SNAPSHOT_EVIDENCE_REVIEW_COLUMNS = [
    "Snapshot_Evidence_Class",
    "Snapshot_Result_Count",
    "Unique_Snapshot_Query_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Evidence_Diagnostic",
]


def build_snapshot_evidence_review(snapshot_results: pd.DataFrame) -> pd.DataFrame:
    if snapshot_results.empty:
        return pd.DataFrame(columns=SNAPSHOT_EVIDENCE_REVIEW_COLUMNS)
    rows = []
    for evidence_class, group in snapshot_results.groupby("Snapshot_Evidence_Class", dropna=False):
        rows.append(
            {
                "Snapshot_Evidence_Class": evidence_class,
                "Snapshot_Result_Count": len(group),
                "Unique_Snapshot_Query_Count": group["Snapshot_Query_ID"].nunique(),
                "Core_Reference_Count": int((group["Matched_Reference_Tier"] == "CORE_REFERENCE").sum()),
                "Supporting_Reference_Count": int((group["Matched_Reference_Tier"] == "SUPPORTING_REFERENCE").sum()),
                "Average_Outcome_Sample_Size": round(
                    pd.to_numeric(group["Matched_Outcome_Sample_Size"], errors="coerce").fillna(0).mean(), 4
                ),
                "Average_Outcome_Dispersion_Pips": round(
                    pd.to_numeric(group["Matched_Outcome_Dispersion_Pips"], errors="coerce").fillna(0).mean(), 4
                ),
                "Evidence_Diagnostic": _diagnostic(str(evidence_class), len(group)),
            }
        )
    return pd.DataFrame(rows, columns=SNAPSHOT_EVIDENCE_REVIEW_COLUMNS)


def _diagnostic(evidence_class: str, count: int) -> str:
    if evidence_class == "CORE_SNAPSHOT_REFERENCE_EVIDENCE":
        return f"{count} descriptive snapshot references meet core evidence criteria."
    if evidence_class == "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE":
        return f"{count} descriptive snapshot references meet supporting evidence criteria."
    if evidence_class == "INSUFFICIENT_SNAPSHOT_REFERENCE_EVIDENCE":
        return f"{count} snapshot query results have insufficient descriptive reference evidence."
    if evidence_class == "INPUT_MISSING":
        return "Snapshot query inputs were missing."
    return f"{count} descriptive snapshot references require review."
