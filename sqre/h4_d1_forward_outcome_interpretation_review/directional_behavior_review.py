"""Directional behavior review for H4/D1 forward outcome profiles."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)


DIRECTIONAL_COLUMNS = [
    "Outcome_Profile_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Up_Move_Count",
    "Down_Move_Count",
    "Flat_Move_Count",
    "Up_Move_Ratio",
    "Down_Move_Ratio",
    "Flat_Move_Ratio",
    "Directional_Imbalance_Ratio",
    "Dominant_Observed_Direction",
    "Directional_Behavior_Class",
    "Directional_Behavior_Diagnostic",
]


def build_directional_behavior_review(
    profiles: pd.DataFrame,
    config: H4D1ForwardOutcomeInterpretationReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=DIRECTIONAL_COLUMNS)
    rows = [_row(profile, config) for _, profile in profiles.iterrows()]
    return pd.DataFrame(rows, columns=DIRECTIONAL_COLUMNS)


def classify_directional_behavior(profile: pd.Series, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> tuple[str, str]:
    sample_size = _int(profile.get("Outcome_Sample_Size"))
    if sample_size < config.minimum_moderate_sample_size:
        return "INSUFFICIENT_SAMPLE", "SAMPLE_CONSTRAINED_DIRECTIONAL_BEHAVIOR"
    up_ratio = _float(profile.get("Up_Move_Ratio"))
    down_ratio = _float(profile.get("Down_Move_Ratio"))
    flat_ratio = _float(profile.get("Flat_Move_Ratio"))
    if flat_ratio >= config.directional_imbalance_threshold and max(up_ratio, down_ratio) < config.directional_imbalance_threshold:
        return "OBSERVED_FLAT_OR_LOW_MOVEMENT", "OBSERVED_FLAT_OR_LOW_DIRECTIONAL_BEHAVIOR"
    if up_ratio >= config.directional_imbalance_threshold and up_ratio > down_ratio:
        return "OBSERVED_UPWARD", "OBSERVED_UPWARD_FOLLOW_THROUGH_DOMINANCE"
    if down_ratio >= config.directional_imbalance_threshold and down_ratio > up_ratio:
        return "OBSERVED_DOWNWARD", "OBSERVED_DOWNWARD_FOLLOW_THROUGH_DOMINANCE"
    return "OBSERVED_MIXED", "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR"


def _row(profile: pd.Series, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> dict[str, object]:
    dominant, behavior = classify_directional_behavior(profile, config)
    up_ratio = _float(profile.get("Up_Move_Ratio"))
    down_ratio = _float(profile.get("Down_Move_Ratio"))
    flat_ratio = _float(profile.get("Flat_Move_Ratio"))
    return {
        "Outcome_Profile_ID": profile.get("Outcome_Profile_ID", ""),
        "Context_Granularity": profile.get("Context_Granularity", ""),
        "H4_Transition_Label": profile.get("H4_Transition_Label", ""),
        "D1_Market_State": profile.get("D1_Market_State", ""),
        "D1_Regime_Label": profile.get("D1_Regime_Label", ""),
        "Forward_Horizon_H4_Candles": _int(profile.get("Forward_Horizon_H4_Candles")),
        "Outcome_Sample_Size": _int(profile.get("Outcome_Sample_Size")),
        "Up_Move_Count": _int(profile.get("Up_Move_Count")),
        "Down_Move_Count": _int(profile.get("Down_Move_Count")),
        "Flat_Move_Count": _int(profile.get("Flat_Move_Count")),
        "Up_Move_Ratio": up_ratio,
        "Down_Move_Ratio": down_ratio,
        "Flat_Move_Ratio": flat_ratio,
        "Directional_Imbalance_Ratio": round(max(up_ratio, down_ratio, flat_ratio), 6),
        "Dominant_Observed_Direction": dominant,
        "Directional_Behavior_Class": behavior,
        "Directional_Behavior_Diagnostic": _diagnostic(behavior),
    }


def _diagnostic(behavior: str) -> str:
    diagnostics = {
        "OBSERVED_UPWARD_FOLLOW_THROUGH_DOMINANCE": "Historical profile shows observed upward follow-through dominance.",
        "OBSERVED_DOWNWARD_FOLLOW_THROUGH_DOMINANCE": "Historical profile shows observed downward follow-through dominance.",
        "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR": "Historical profile shows mixed directional behavior.",
        "OBSERVED_FLAT_OR_LOW_DIRECTIONAL_BEHAVIOR": "Historical profile shows flat or low directional behavior.",
        "SAMPLE_CONSTRAINED_DIRECTIONAL_BEHAVIOR": "Directional behavior is constrained by sample size.",
    }
    return diagnostics[behavior]


def _int(value: object) -> int:
    number = pd.to_numeric(value, errors="coerce")
    return int(number) if pd.notna(number) else 0


def _float(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return round(float(number), 6) if pd.notna(number) else 0.0
