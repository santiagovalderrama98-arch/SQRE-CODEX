"""Descriptive behavior panel for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.dashboard_panel_builder import count_value, first_value, reindex, unique_count


BEHAVIOR_PANEL_COLUMNS = [
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
    "Panel_Status",
]


def build_behavior_panel(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    behavior = frames.get("snapshot_behavior_summary", pd.DataFrame())
    queries = frames.get("snapshot_query_requests", pd.DataFrame())
    results = frames.get("snapshot_reference_results", pd.DataFrame())
    if behavior.empty and queries.empty and results.empty:
        return reindex(pd.DataFrame(), BEHAVIOR_PANEL_COLUMNS)
    row = {
        "Snapshot_ID": first_value(behavior, ["Snapshot_ID"], "LATEST_AVAILABLE_SNAPSHOT"),
        "Snapshot_Query_Count": int(first_value(behavior, ["Snapshot_Query_Count"], len(queries))),
        "Snapshot_Result_Count": int(first_value(behavior, ["Snapshot_Result_Count"], len(results))),
        "Matched_Horizon_Count": int(first_value(behavior, ["Matched_Horizon_Count"], unique_count(results, "Matched_Forward_Horizon_H4_Candles"))),
        "Primary_Matched_Horizon": first_value(
            behavior, ["Primary_Matched_Horizon"], first_value(results, ["Matched_Forward_Horizon_H4_Candles"], "")
        ),
        "Primary_Match_Level": first_value(behavior, ["Primary_Match_Level"], first_value(results, ["Snapshot_Query_Match_Level"], "")),
        "Primary_Evidence_Class": first_value(behavior, ["Primary_Evidence_Class"], first_value(results, ["Snapshot_Evidence_Class"], "")),
        "High_Evidence_Result_Count": int(
            first_value(
                behavior,
                ["High_Evidence_Result_Count"],
                count_value(results, "Snapshot_Research_Result_Class", "HIGH_EVIDENCE_SNAPSHOT_REFERENCE"),
            )
        ),
        "Moderate_Evidence_Result_Count": int(
            first_value(
                behavior,
                ["Moderate_Evidence_Result_Count"],
                count_value(results, "Snapshot_Research_Result_Class", "MODERATE_EVIDENCE_SNAPSHOT_REFERENCE"),
            )
        ),
        "Low_Evidence_Result_Count": int(
            first_value(
                behavior,
                ["Low_Evidence_Result_Count"],
                count_value(results, "Snapshot_Research_Result_Class", "LOW_EVIDENCE_SNAPSHOT_REFERENCE"),
            )
        ),
        "No_Usable_Result_Count": int(
            first_value(
                behavior,
                ["No_Usable_Result_Count"],
                count_value(results, "Snapshot_Research_Result_Class", "NO_USABLE_SNAPSHOT_REFERENCE"),
            )
        ),
        "Core_Evidence_Result_Count": int(
            first_value(
                behavior,
                ["Core_Evidence_Result_Count"],
                count_value(results, "Snapshot_Evidence_Class", "CORE_SNAPSHOT_REFERENCE_EVIDENCE"),
            )
        ),
        "Supporting_Evidence_Result_Count": int(
            first_value(
                behavior,
                ["Supporting_Evidence_Result_Count"],
                count_value(results, "Snapshot_Evidence_Class", "SUPPORTING_SNAPSHOT_REFERENCE_EVIDENCE"),
            )
        ),
        "Observed_Direction_Class_Count": int(
            first_value(behavior, ["Observed_Direction_Class_Count"], unique_count(results, "Matched_Directional_Behavior_Class"))
        ),
        "Dominant_Observed_Direction_Count": int(
            first_value(behavior, ["Dominant_Observed_Direction_Count"], unique_count(results, "Matched_Dominant_Observed_Direction"))
        ),
        "Behavior_Summary_Diagnostic": "Descriptive behavior counts from local snapshot outputs.",
        "Panel_Status": "PANEL_READY",
    }
    return reindex(pd.DataFrame([row]), BEHAVIOR_PANEL_COLUMNS)
