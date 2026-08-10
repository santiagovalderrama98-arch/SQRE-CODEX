"""Historical reference cards for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.dashboard_panel_builder import reindex, row_value


REFERENCE_CARD_COLUMNS = [
    "Reference_Card_ID",
    "Snapshot_Query_ID",
    "Requested_Forward_Horizon_H4_Candles",
    "Matched_Research_Reference_ID",
    "Matched_Outcome_Profile_ID",
    "Matched_Context_Granularity",
    "Matched_Reference_Tier",
    "Matched_Forward_Horizon_H4_Candles",
    "Matched_Outcome_Sample_Size",
    "Matched_Outcome_Dispersion_Pips",
    "Matched_Mean_Forward_Close_Change_Pips",
    "Matched_Median_Forward_Close_Change_Pips",
    "Matched_Directional_Behavior_Class",
    "Matched_Dominant_Observed_Direction",
    "Matched_Excursion_Behavior_Class",
    "Matched_Horizon_Stability_Class",
    "Snapshot_Query_Match_Level",
    "Snapshot_Research_Result_Class",
    "Snapshot_Evidence_Class",
    "Result_Rank",
    "Card_Diagnostic",
]


def build_reference_cards(frames: dict[str, pd.DataFrame], config: ResearchDashboardPrototypeConfig) -> pd.DataFrame:
    results = frames.get("snapshot_reference_results", pd.DataFrame())
    if results.empty:
        return reindex(pd.DataFrame(), REFERENCE_CARD_COLUMNS)
    records = []
    selected = _ranked(_usable_reference_results(results)).head(config.maximum_reference_cards)
    for index, (_, row) in enumerate(selected.iterrows(), start=1):
        records.append(
            {
                "Reference_Card_ID": f"REF_CARD_{index:06d}",
                "Snapshot_Query_ID": row_value(row, ["Snapshot_Query_ID"]),
                "Requested_Forward_Horizon_H4_Candles": row_value(row, ["Requested_Forward_Horizon_H4_Candles"]),
                "Matched_Research_Reference_ID": row_value(row, ["Matched_Research_Reference_ID"]),
                "Matched_Outcome_Profile_ID": row_value(row, ["Matched_Outcome_Profile_ID"]),
                "Matched_Context_Granularity": row_value(row, ["Matched_Context_Granularity"]),
                "Matched_Reference_Tier": row_value(row, ["Matched_Reference_Tier"]),
                "Matched_Forward_Horizon_H4_Candles": row_value(row, ["Matched_Forward_Horizon_H4_Candles"]),
                "Matched_Outcome_Sample_Size": row_value(row, ["Matched_Outcome_Sample_Size"]),
                "Matched_Outcome_Dispersion_Pips": row_value(row, ["Matched_Outcome_Dispersion_Pips"]),
                "Matched_Mean_Forward_Close_Change_Pips": row_value(row, ["Matched_Mean_Forward_Close_Change_Pips"]),
                "Matched_Median_Forward_Close_Change_Pips": row_value(row, ["Matched_Median_Forward_Close_Change_Pips"]),
                "Matched_Directional_Behavior_Class": row_value(row, ["Matched_Directional_Behavior_Class"]),
                "Matched_Dominant_Observed_Direction": row_value(row, ["Matched_Dominant_Observed_Direction"]),
                "Matched_Excursion_Behavior_Class": row_value(row, ["Matched_Excursion_Behavior_Class"]),
                "Matched_Horizon_Stability_Class": row_value(row, ["Matched_Horizon_Stability_Class"]),
                "Snapshot_Query_Match_Level": row_value(row, ["Snapshot_Query_Match_Level"]),
                "Snapshot_Research_Result_Class": row_value(row, ["Snapshot_Research_Result_Class"]),
                "Snapshot_Evidence_Class": row_value(row, ["Snapshot_Evidence_Class"]),
                "Result_Rank": row_value(row, ["Result_Rank"], index),
                "Card_Diagnostic": "Descriptive historical reference card.",
            }
        )
    return reindex(pd.DataFrame(records), REFERENCE_CARD_COLUMNS)


def _usable_reference_results(results: pd.DataFrame) -> pd.DataFrame:
    if "Matched_Research_Reference_ID" not in results.columns:
        return results
    usable = results[results["Matched_Research_Reference_ID"].fillna("").astype(str) != ""].copy()
    if "Snapshot_Research_Result_Class" in usable.columns:
        usable = usable[usable["Snapshot_Research_Result_Class"].astype(str) != "NO_USABLE_SNAPSHOT_REFERENCE"]
    return usable


def _ranked(results: pd.DataFrame) -> pd.DataFrame:
    if "Result_Rank" not in results.columns:
        return results
    ranked = results.copy()
    ranked["_rank"] = pd.to_numeric(ranked["Result_Rank"], errors="coerce").fillna(999999)
    return ranked.sort_values(["_rank"]).drop(columns=["_rank"])
