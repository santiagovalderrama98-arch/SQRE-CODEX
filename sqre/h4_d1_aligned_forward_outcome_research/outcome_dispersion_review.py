"""Review forward outcome dispersion."""

from __future__ import annotations

import pandas as pd


DISPERSION_REVIEW_COLUMNS = [
    "Outcome_Profile_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Mean_Forward_Close_Change_Pips",
    "Median_Forward_Close_Change_Pips",
    "Outcome_Dispersion_Pips",
    "Directional_Balance_Diagnostic",
    "Outcome_Dispersion_Class",
    "Dispersion_Diagnostic",
]


def build_dispersion_review(outcome_profiles: pd.DataFrame) -> pd.DataFrame:
    if outcome_profiles.empty:
        return pd.DataFrame(columns=DISPERSION_REVIEW_COLUMNS)
    rows = []
    for _, row in outcome_profiles.iterrows():
        dispersion_class = classify_outcome_dispersion(float(row["Outcome_Dispersion_Pips"]))
        rows.append(
            {
                "Outcome_Profile_ID": row["Outcome_Profile_ID"],
                "Context_Granularity": row["Context_Granularity"],
                "H4_Transition_Label": row["H4_Transition_Label"],
                "D1_Market_State": row["D1_Market_State"],
                "D1_Regime_Label": row["D1_Regime_Label"],
                "Forward_Horizon_H4_Candles": row["Forward_Horizon_H4_Candles"],
                "Outcome_Sample_Size": row["Outcome_Sample_Size"],
                "Mean_Forward_Close_Change_Pips": row["Mean_Forward_Close_Change_Pips"],
                "Median_Forward_Close_Change_Pips": row["Median_Forward_Close_Change_Pips"],
                "Outcome_Dispersion_Pips": row["Outcome_Dispersion_Pips"],
                "Directional_Balance_Diagnostic": _directional_balance(row),
                "Outcome_Dispersion_Class": dispersion_class,
                "Dispersion_Diagnostic": _diagnostic(dispersion_class),
            }
        )
    return pd.DataFrame(rows, columns=DISPERSION_REVIEW_COLUMNS)


def classify_outcome_dispersion(dispersion_pips: float) -> str:
    if pd.isna(dispersion_pips):
        return "INPUT_MISSING"
    if dispersion_pips < 5:
        return "LOW_OUTCOME_DISPERSION"
    if dispersion_pips < 15:
        return "MODERATE_OUTCOME_DISPERSION"
    if dispersion_pips < 30:
        return "HIGH_OUTCOME_DISPERSION"
    return "EXTREME_OUTCOME_DISPERSION"


def _directional_balance(row: pd.Series) -> str:
    up = float(row["Up_Move_Ratio"])
    down = float(row["Down_Move_Ratio"])
    if abs(up - down) <= 0.20:
        return "Forward direction counts are broadly balanced."
    if up > down:
        return "Forward direction counts lean upward descriptively."
    return "Forward direction counts lean downward descriptively."


def _diagnostic(dispersion_class: str) -> str:
    if dispersion_class == "LOW_OUTCOME_DISPERSION":
        return "Forward close changes are tightly clustered."
    if dispersion_class == "MODERATE_OUTCOME_DISPERSION":
        return "Forward close changes show moderate spread."
    if dispersion_class == "HIGH_OUTCOME_DISPERSION":
        return "Forward close changes show high spread."
    if dispersion_class == "EXTREME_OUTCOME_DISPERSION":
        return "Forward close changes show extreme spread."
    return "Dispersion input is missing."
