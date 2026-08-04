"""Excursion behavior review for H4/D1 forward outcome profiles."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)


EXCURSION_COLUMNS = [
    "Outcome_Profile_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Mean_Forward_High_Excursion_Pips",
    "Mean_Forward_Low_Excursion_Pips",
    "Mean_Forward_Range_Pips",
    "Excursion_Imbalance_Pips",
    "Excursion_Behavior_Class",
    "Excursion_Behavior_Diagnostic",
]


def build_excursion_behavior_review(
    profiles: pd.DataFrame,
    config: H4D1ForwardOutcomeInterpretationReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=EXCURSION_COLUMNS)
    rows = [_row(profile, config) for _, profile in profiles.iterrows()]
    return pd.DataFrame(rows, columns=EXCURSION_COLUMNS)


def classify_excursion_behavior(profile: pd.Series, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> str:
    sample_size = _int(profile.get("Outcome_Sample_Size"))
    if sample_size < config.minimum_moderate_sample_size:
        return "SAMPLE_CONSTRAINED_EXCURSION_BEHAVIOR"
    high = abs(_float(profile.get("Mean_Forward_High_Excursion_Pips")))
    low = abs(_float(profile.get("Mean_Forward_Low_Excursion_Pips")))
    range_pips = _float(profile.get("Mean_Forward_Range_Pips"))
    if range_pips >= config.high_dispersion_threshold_pips:
        return "HIGH_RANGE_EXPANSION_BEHAVIOR"
    imbalance = high - low
    if imbalance >= 2.0:
        return "UPSIDE_EXCURSION_DOMINANT"
    if imbalance <= -2.0:
        return "DOWNSIDE_EXCURSION_DOMINANT"
    return "BALANCED_EXCURSION_BEHAVIOR"


def _row(profile: pd.Series, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> dict[str, object]:
    high = abs(_float(profile.get("Mean_Forward_High_Excursion_Pips")))
    low = abs(_float(profile.get("Mean_Forward_Low_Excursion_Pips")))
    behavior = classify_excursion_behavior(profile, config)
    return {
        "Outcome_Profile_ID": profile.get("Outcome_Profile_ID", ""),
        "Context_Granularity": profile.get("Context_Granularity", ""),
        "H4_Transition_Label": profile.get("H4_Transition_Label", ""),
        "D1_Market_State": profile.get("D1_Market_State", ""),
        "D1_Regime_Label": profile.get("D1_Regime_Label", ""),
        "Forward_Horizon_H4_Candles": _int(profile.get("Forward_Horizon_H4_Candles")),
        "Outcome_Sample_Size": _int(profile.get("Outcome_Sample_Size")),
        "Mean_Forward_High_Excursion_Pips": _float(profile.get("Mean_Forward_High_Excursion_Pips")),
        "Mean_Forward_Low_Excursion_Pips": _float(profile.get("Mean_Forward_Low_Excursion_Pips")),
        "Mean_Forward_Range_Pips": _float(profile.get("Mean_Forward_Range_Pips")),
        "Excursion_Imbalance_Pips": round(high - low, 6),
        "Excursion_Behavior_Class": behavior,
        "Excursion_Behavior_Diagnostic": _diagnostic(behavior),
    }


def _diagnostic(behavior: str) -> str:
    diagnostics = {
        "UPSIDE_EXCURSION_DOMINANT": "Upside excursion is larger in the historical profile.",
        "DOWNSIDE_EXCURSION_DOMINANT": "Downside excursion is larger in the historical profile.",
        "BALANCED_EXCURSION_BEHAVIOR": "Upside and downside excursions are broadly balanced.",
        "HIGH_RANGE_EXPANSION_BEHAVIOR": "Forward range expansion is high in the historical profile.",
        "SAMPLE_CONSTRAINED_EXCURSION_BEHAVIOR": "Excursion behavior is constrained by sample size.",
    }
    return diagnostics[behavior]


def _int(value: object) -> int:
    number = pd.to_numeric(value, errors="coerce")
    return int(number) if pd.notna(number) else 0


def _float(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return round(float(number), 6) if pd.notna(number) else 0.0
