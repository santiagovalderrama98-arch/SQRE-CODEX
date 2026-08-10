"""Evidence summary panel for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.dashboard_panel_builder import numeric_mean, reindex, unique_count


EVIDENCE_PANEL_COLUMNS = [
    "Snapshot_Evidence_Class",
    "Snapshot_Result_Count",
    "Unique_Snapshot_Query_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Average_Outcome_Sample_Size",
    "Average_Outcome_Dispersion_Pips",
    "Evidence_Diagnostic",
    "Panel_Status",
]


def build_evidence_panel(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    results = frames.get("snapshot_reference_results", pd.DataFrame())
    if results.empty or "Snapshot_Evidence_Class" not in results.columns:
        return reindex(pd.DataFrame(), EVIDENCE_PANEL_COLUMNS)
    rows = []
    for evidence_class, group in results.groupby("Snapshot_Evidence_Class", dropna=False):
        rows.append(
            {
                "Snapshot_Evidence_Class": str(evidence_class),
                "Snapshot_Result_Count": len(group),
                "Unique_Snapshot_Query_Count": unique_count(group, "Snapshot_Query_ID"),
                "Core_Reference_Count": int((group["Snapshot_Evidence_Class"].astype(str) == "CORE_SNAPSHOT_REFERENCE_EVIDENCE").sum()),
                "Supporting_Reference_Count": int(
                    (group["Snapshot_Evidence_Class"].astype(str) == "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE").sum()
                ),
                "Average_Outcome_Sample_Size": numeric_mean(group, "Matched_Outcome_Sample_Size"),
                "Average_Outcome_Dispersion_Pips": numeric_mean(group, "Matched_Outcome_Dispersion_Pips"),
                "Evidence_Diagnostic": "Evidence class summarized from local snapshot reference results.",
                "Panel_Status": "PANEL_READY",
            }
        )
    return reindex(pd.DataFrame(rows), EVIDENCE_PANEL_COLUMNS)
