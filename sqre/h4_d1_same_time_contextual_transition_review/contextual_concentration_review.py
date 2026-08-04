"""Review concentration of H4 transitions under D1 contexts."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.d1_context_distribution_review import classify_distribution


CONCENTRATION_COLUMNS = [
    "H4_Transition_Label",
    "Transition_Total_Count",
    "Distinct_D1_Market_State_Count",
    "Distinct_D1_Regime_Count",
    "Dominant_D1_Market_State",
    "Dominant_D1_Market_State_Count",
    "Dominant_D1_Market_State_Share",
    "Dominant_D1_Regime_Label",
    "Dominant_D1_Regime_Count",
    "Dominant_D1_Regime_Share",
    "Transition_Context_Distribution_Class",
    "Concentration_Diagnostic",
]


def build_context_concentration_review(
    profiles: pd.DataFrame,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=CONCENTRATION_COLUMNS)
    rows: list[dict[str, object]] = []
    for transition_label, group in profiles.groupby("H4_Transition_Label", dropna=False):
        total = int(group["Context_Row_Count"].sum())
        state_counts = group.groupby("D1_Market_State")["Context_Row_Count"].sum().sort_values(ascending=False)
        regime_counts = group.groupby("D1_Regime_Label")["Context_Row_Count"].sum().sort_values(ascending=False)
        state_name, state_count = _dominant(state_counts)
        regime_name, regime_count = _dominant(regime_counts)
        state_share = round(state_count / total, 6) if total else 0.0
        regime_share = round(regime_count / total, 6) if total else 0.0
        dominant_share = max(state_share, regime_share)
        distribution_class = classify_distribution(
            total,
            dominant_share,
            max(int(group["D1_Market_State"].nunique()), int(group["D1_Regime_Label"].nunique())),
            config,
        )
        rows.append(
            {
                "H4_Transition_Label": transition_label,
                "Transition_Total_Count": total,
                "Distinct_D1_Market_State_Count": int(group["D1_Market_State"].nunique()),
                "Distinct_D1_Regime_Count": int(group["D1_Regime_Label"].nunique()),
                "Dominant_D1_Market_State": state_name,
                "Dominant_D1_Market_State_Count": state_count,
                "Dominant_D1_Market_State_Share": state_share,
                "Dominant_D1_Regime_Label": regime_name,
                "Dominant_D1_Regime_Count": regime_count,
                "Dominant_D1_Regime_Share": regime_share,
                "Transition_Context_Distribution_Class": distribution_class,
                "Concentration_Diagnostic": _diagnostic(distribution_class),
            }
        )
    return pd.DataFrame(rows, columns=CONCENTRATION_COLUMNS)


def _dominant(counts: pd.Series) -> tuple[str, int]:
    if counts.empty:
        return "", 0
    return str(counts.index[0]), int(counts.iloc[0])


def _diagnostic(distribution_class: str) -> str:
    if distribution_class == "D1_CONTEXT_CONCENTRATED":
        return "One same-time D1 context contains most observations for this H4 transition."
    if distribution_class == "D1_CONTEXT_DISPERSED":
        return "Observations are spread across several same-time D1 contexts."
    if distribution_class == "D1_CONTEXT_MIXED":
        return "Observations are split across a limited set of same-time D1 contexts."
    if distribution_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "Transition sample is constrained for concentration review."
    return "Concentration input is missing."
