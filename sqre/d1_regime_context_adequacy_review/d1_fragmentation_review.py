"""Review D1 context fragmentation by H4 transition."""

from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig


FRAGMENTATION_COLUMNS = [
    "H4_Transition_Label",
    "Transition_Total_Count",
    "Distinct_D1_Market_State_Count",
    "Distinct_D1_Regime_Count",
    "Distinct_Context_Profile_Count",
    "Research_Ready_Context_Count",
    "Low_Or_Insufficient_Context_Count",
    "Fragmentation_Ratio",
    "Dominant_D1_Market_State",
    "Dominant_D1_Market_State_Share",
    "Dominant_D1_Regime_Label",
    "Dominant_D1_Regime_Share",
    "D1_Fragmentation_Class",
    "Fragmentation_Diagnostic",
]


def build_fragmentation_review(
    profiles: pd.DataFrame,
    concentration_review: pd.DataFrame,
    config: D1RegimeContextAdequacyReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=FRAGMENTATION_COLUMNS)
    concentration_by_transition = _concentration_lookup(concentration_review)
    rows = []
    for transition_label, group in profiles.groupby("H4_Transition_Label", dropna=False):
        profile_count = len(group)
        low_count = int(
            group["Context_Sample_Adequacy_Class"].isin(["LOW_CONTEXT_SAMPLE", "INSUFFICIENT_CONTEXT_SAMPLE"]).sum()
        )
        ready_count = int((group["Context_Sample_Adequacy_Class"] == "RESEARCH_READY_CONTEXT_SAMPLE").sum())
        ratio = round(low_count / profile_count, 6) if profile_count else 0.0
        row = concentration_by_transition.get(str(transition_label), {})
        fragmentation_class = classify_fragmentation(ratio, profile_count, config)
        rows.append(
            {
                "H4_Transition_Label": transition_label,
                "Transition_Total_Count": int(group["Transition_Total_Count"].max()),
                "Distinct_D1_Market_State_Count": int(group["D1_Market_State"].nunique()),
                "Distinct_D1_Regime_Count": int(group["D1_Regime_Label"].nunique()),
                "Distinct_Context_Profile_Count": profile_count,
                "Research_Ready_Context_Count": ready_count,
                "Low_Or_Insufficient_Context_Count": low_count,
                "Fragmentation_Ratio": ratio,
                "Dominant_D1_Market_State": row.get("Dominant_D1_Market_State", ""),
                "Dominant_D1_Market_State_Share": row.get("Dominant_D1_Market_State_Share", 0.0),
                "Dominant_D1_Regime_Label": row.get("Dominant_D1_Regime_Label", ""),
                "Dominant_D1_Regime_Share": row.get("Dominant_D1_Regime_Share", 0.0),
                "D1_Fragmentation_Class": fragmentation_class,
                "Fragmentation_Diagnostic": _diagnostic(fragmentation_class),
            }
        )
    return pd.DataFrame(rows, columns=FRAGMENTATION_COLUMNS)


def classify_fragmentation(
    fragmentation_ratio: float,
    profile_count: int,
    config: D1RegimeContextAdequacyReviewConfig,
) -> str:
    if profile_count <= 0:
        return "INPUT_MISSING"
    if fragmentation_ratio >= 0.90:
        return "EXTREME_D1_CONTEXT_FRAGMENTATION"
    if fragmentation_ratio >= config.fragmentation_ratio_threshold:
        return "HIGH_D1_CONTEXT_FRAGMENTATION"
    if fragmentation_ratio >= 0.40:
        return "MODERATE_D1_CONTEXT_FRAGMENTATION"
    return "LOW_D1_CONTEXT_FRAGMENTATION"


def _concentration_lookup(concentration_review: pd.DataFrame) -> dict[str, dict[str, object]]:
    if concentration_review.empty or "H4_Transition_Label" not in concentration_review.columns:
        return {}
    return {str(row["H4_Transition_Label"]): row.to_dict() for _, row in concentration_review.iterrows()}


def _diagnostic(fragmentation_class: str) -> str:
    if fragmentation_class == "LOW_D1_CONTEXT_FRAGMENTATION":
        return "D1 context segmentation preserves H4 transition sample adequacy."
    if fragmentation_class == "MODERATE_D1_CONTEXT_FRAGMENTATION":
        return "D1 context segmentation creates some constrained profiles."
    if fragmentation_class == "HIGH_D1_CONTEXT_FRAGMENTATION":
        return "D1 context segmentation creates many constrained H4 profiles."
    if fragmentation_class == "EXTREME_D1_CONTEXT_FRAGMENTATION":
        return "D1 context segmentation is dominated by constrained H4 profiles."
    return "Fragmentation input is missing."
