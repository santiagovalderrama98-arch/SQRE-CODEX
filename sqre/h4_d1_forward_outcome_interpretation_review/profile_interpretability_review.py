"""Profile interpretability review for H4/D1 forward outcomes."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)


INTERPRETABILITY_COLUMNS = [
    "Outcome_Profile_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
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
    "Interpretability_Diagnostic",
]

PROFILE_KEY_COLUMNS = [
    "Outcome_Profile_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Forward_Horizon_H4_Candles",
]


def build_profile_interpretability_review(
    profiles: pd.DataFrame,
    config: H4D1ForwardOutcomeInterpretationReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=INTERPRETABILITY_COLUMNS)
    rows = []
    for _, profile in profiles.iterrows():
        rows.append(_row(profile, config))
    return pd.DataFrame(rows, columns=INTERPRETABILITY_COLUMNS)


def classify_interpretability(profile: pd.Series, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> str:
    sample_size = _int(profile.get("Outcome_Sample_Size"))
    dispersion = _float(profile.get("Outcome_Dispersion_Pips"))
    if sample_size <= 0:
        return "INPUT_MISSING"
    if sample_size < config.minimum_moderate_sample_size:
        return "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED"
    if dispersion >= config.extreme_dispersion_threshold_pips:
        return "NOT_INTERPRETABLE_HIGH_DISPERSION"
    if sample_size >= config.minimum_interpretation_sample_size and dispersion < config.high_dispersion_threshold_pips:
        return "INTERPRETABLE_OUTCOME_PROFILE"
    if sample_size >= config.minimum_moderate_sample_size and dispersion < config.extreme_dispersion_threshold_pips:
        return "MODERATELY_INTERPRETABLE_OUTCOME_PROFILE"
    return "LOW_INTERPRETABILITY_OUTCOME_PROFILE"


def _row(profile: pd.Series, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> dict[str, object]:
    interpretability = classify_interpretability(profile, config)
    return {
        **{column: profile.get(column, "") for column in PROFILE_KEY_COLUMNS},
        "Outcome_Sample_Size": _int(profile.get("Outcome_Sample_Size")),
        "Mean_Forward_Close_Change_Pips": _float(profile.get("Mean_Forward_Close_Change_Pips")),
        "Median_Forward_Close_Change_Pips": _float(profile.get("Median_Forward_Close_Change_Pips")),
        "Outcome_Dispersion_Pips": _float(profile.get("Outcome_Dispersion_Pips")),
        "Outcome_Sample_Adequacy_Class": profile.get("Outcome_Sample_Adequacy_Class", ""),
        "Outcome_Interpretability_Class": interpretability,
        "Interpretability_Diagnostic": _diagnostic(interpretability),
    }


def _diagnostic(interpretability: str) -> str:
    diagnostics = {
        "INTERPRETABLE_OUTCOME_PROFILE": "Profile has sufficient sample depth and contained dispersion.",
        "MODERATELY_INTERPRETABLE_OUTCOME_PROFILE": "Profile has moderate interpretability for descriptive review.",
        "LOW_INTERPRETABILITY_OUTCOME_PROFILE": "Profile has limited interpretability.",
        "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED": "Profile is constrained by sample size.",
        "NOT_INTERPRETABLE_HIGH_DISPERSION": "Profile is constrained by high outcome dispersion.",
        "INPUT_MISSING": "Profile input is missing or empty.",
    }
    return diagnostics[interpretability]


def _int(value: object) -> int:
    number = pd.to_numeric(value, errors="coerce")
    return int(number) if pd.notna(number) else 0


def _float(value: object) -> float:
    number = pd.to_numeric(value, errors="coerce")
    return round(float(number), 6) if pd.notna(number) else 0.0
