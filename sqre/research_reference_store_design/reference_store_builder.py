"""Build the included Research Reference Store artifact."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_design.reference_tier_classifier import INCLUDED_STATUS


STORE_COLUMNS = [
    "Research_Reference_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Outcome_Profile_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Mean_Forward_Close_Change_Pips",
    "Median_Forward_Close_Change_Pips",
    "Outcome_Dispersion_Pips",
    "Outcome_Interpretability_Class",
    "Directional_Behavior_Class",
    "Dominant_Observed_Direction",
    "Excursion_Behavior_Class",
    "Horizon_Stability_Class",
    "Reference_Tier",
    "Research_Reference_Diagnostic",
]


def build_reference_store(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(columns=STORE_COLUMNS)
    included = candidates[candidates["Reference_Inclusion_Status"] == INCLUDED_STATUS].copy()
    rows = []
    for sequence, (_, row) in enumerate(included.iterrows(), start=1):
        record = {column: row.get(column, "") for column in STORE_COLUMNS if column != "Research_Reference_ID"}
        record["Research_Reference_ID"] = f"RRS_{sequence:06d}"
        record["Research_Reference_Diagnostic"] = row.get("Reference_Diagnostic", "")
        rows.append(record)
    return pd.DataFrame(rows, columns=STORE_COLUMNS)
