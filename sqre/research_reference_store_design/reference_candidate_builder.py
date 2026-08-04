"""Build research reference candidates from interpreted profile reviews."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.reference_tier_classifier import classify_reference_tier


CANDIDATE_COLUMNS = [
    "Research_Reference_Candidate_ID",
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
    "Outcome_Sample_Adequacy_Class",
    "Outcome_Interpretability_Class",
    "Directional_Behavior_Class",
    "Dominant_Observed_Direction",
    "Excursion_Behavior_Class",
    "Horizon_Stability_Class",
    "Reference_Tier",
    "Reference_Inclusion_Status",
    "Reference_Diagnostic",
]

PROFILE_ID = "Outcome_Profile_ID"
HORIZON_KEYS = ["Context_Granularity", "H4_Transition_Label", "D1_Market_State", "D1_Regime_Label"]


def build_reference_candidates(
    interpretability_review: pd.DataFrame,
    directional_behavior_review: pd.DataFrame,
    excursion_behavior_review: pd.DataFrame,
    horizon_stability_review: pd.DataFrame,
    config: ResearchReferenceStoreDesignConfig,
) -> pd.DataFrame:
    if interpretability_review.empty:
        return pd.DataFrame(columns=CANDIDATE_COLUMNS)
    frame = interpretability_review.copy()
    frame = _merge_by_profile(frame, directional_behavior_review, ["Directional_Behavior_Class", "Dominant_Observed_Direction"])
    frame = _merge_by_profile(frame, excursion_behavior_review, ["Excursion_Behavior_Class"])
    frame = _merge_horizon_stability(frame, horizon_stability_review)
    rows = []
    for sequence, (_, row) in enumerate(frame.iterrows(), start=1):
        tier, status, diagnostic = classify_reference_tier(row, config)
        rows.append(
            {
                "Research_Reference_Candidate_ID": f"RRC_{sequence:06d}",
                "Symbol": _value(row, "Symbol", config.symbol),
                "H4_Timeframe": _value(row, "H4_Timeframe", config.h4_timeframe),
                "D1_Timeframe": _value(row, "D1_Timeframe", config.d1_timeframe),
                "Outcome_Profile_ID": _value(row, "Outcome_Profile_ID"),
                "Context_Granularity": _value(row, "Context_Granularity"),
                "H4_Transition_Label": _value(row, "H4_Transition_Label"),
                "D1_Market_State": _value(row, "D1_Market_State"),
                "D1_Regime_Label": _value(row, "D1_Regime_Label"),
                "D1_Structure_Direction": _value(row, "D1_Structure_Direction"),
                "Forward_Horizon_H4_Candles": _int(row.get("Forward_Horizon_H4_Candles")),
                "Outcome_Sample_Size": _int(row.get("Outcome_Sample_Size")),
                "Mean_Forward_Close_Change_Pips": _float(row.get("Mean_Forward_Close_Change_Pips")),
                "Median_Forward_Close_Change_Pips": _float(row.get("Median_Forward_Close_Change_Pips")),
                "Outcome_Dispersion_Pips": _float(row.get("Outcome_Dispersion_Pips")),
                "Outcome_Sample_Adequacy_Class": _value(row, "Outcome_Sample_Adequacy_Class"),
                "Outcome_Interpretability_Class": _value(row, "Outcome_Interpretability_Class"),
                "Directional_Behavior_Class": _value(row, "Directional_Behavior_Class", "INPUT_MISSING"),
                "Dominant_Observed_Direction": _value(row, "Dominant_Observed_Direction", "INPUT_MISSING"),
                "Excursion_Behavior_Class": _value(row, "Excursion_Behavior_Class", "INPUT_MISSING"),
                "Horizon_Stability_Class": _value(row, "Horizon_Stability_Class", "INPUT_MISSING"),
                "Reference_Tier": tier,
                "Reference_Inclusion_Status": status,
                "Reference_Diagnostic": diagnostic,
            }
        )
    return pd.DataFrame(rows, columns=CANDIDATE_COLUMNS)


def _merge_by_profile(frame: pd.DataFrame, other: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if other.empty or PROFILE_ID not in other.columns:
        for column in columns:
            frame[column] = "INPUT_MISSING"
        return frame
    available = [column for column in columns if column in other.columns]
    subset = other[[PROFILE_ID, *available]].drop_duplicates(PROFILE_ID)
    merged = frame.merge(subset, on=PROFILE_ID, how="left")
    for column in columns:
        if column not in merged.columns:
            merged[column] = "INPUT_MISSING"
        else:
            merged[column] = merged[column].fillna("INPUT_MISSING")
    return merged


def _merge_horizon_stability(frame: pd.DataFrame, horizon: pd.DataFrame) -> pd.DataFrame:
    if horizon.empty:
        frame["Horizon_Stability_Class"] = "INPUT_MISSING"
        return frame
    keys = [key for key in HORIZON_KEYS if key in frame.columns and key in horizon.columns]
    if not keys or "Horizon_Stability_Class" not in horizon.columns:
        frame["Horizon_Stability_Class"] = "INPUT_MISSING"
        return frame
    subset = horizon[[*keys, "Horizon_Stability_Class"]].drop_duplicates(keys)
    merged = frame.merge(subset, on=keys, how="left")
    merged["Horizon_Stability_Class"] = merged["Horizon_Stability_Class"].fillna("INPUT_MISSING")
    return merged


def _value(row: pd.Series, column: str, default: str = "") -> str:
    value = row.get(column, default)
    if pd.isna(value):
        return default
    return str(value)


def _int(value: object) -> int:
    number = pd.to_numeric(value, errors="coerce")
    return int(number) if pd.notna(number) else 0


def _float(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return round(float(number), 6) if pd.notna(number) else 0.0
