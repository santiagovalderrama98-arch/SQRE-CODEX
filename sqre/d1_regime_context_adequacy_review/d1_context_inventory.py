"""Build D1 context inventory from contextual transition profiles."""

from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig


D1_CONTEXT_INVENTORY_COLUMNS = [
    "D1_Context_ID",
    "Symbol",
    "D1_Timeframe",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Aligned_H4_Transition_Row_Count",
    "Distinct_H4_Transition_Count",
    "Distinct_Context_Profile_Count",
    "Research_Ready_Context_Count",
    "Low_Or_Insufficient_Context_Count",
    "D1_Context_Adequacy_Class",
    "D1_Context_Diagnostic",
]


def build_d1_context_inventory(
    profiles: pd.DataFrame,
    config: D1RegimeContextAdequacyReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=D1_CONTEXT_INVENTORY_COLUMNS)
    group_columns = ["D1_Market_State", "D1_Regime_Label", "D1_Structure_Direction"]
    rows = []
    for index, (key, group) in enumerate(profiles.groupby(group_columns, dropna=False), start=1):
        market_state, regime, direction = key
        ready_count = int((group["Context_Sample_Adequacy_Class"] == "RESEARCH_READY_CONTEXT_SAMPLE").sum())
        low_count = int(
            group["Context_Sample_Adequacy_Class"].isin(["LOW_CONTEXT_SAMPLE", "INSUFFICIENT_CONTEXT_SAMPLE"]).sum()
        )
        row_count = int(group["Context_Row_Count"].sum())
        adequacy_class = classify_d1_context_adequacy(ready_count, low_count, len(group), row_count)
        rows.append(
            {
                "D1_Context_ID": f"D1_CONTEXT_{index:06d}",
                "Symbol": config.symbol,
                "D1_Timeframe": config.d1_timeframe,
                "D1_Market_State": market_state,
                "D1_Regime_Label": regime,
                "D1_Structure_Direction": direction,
                "Aligned_H4_Transition_Row_Count": row_count,
                "Distinct_H4_Transition_Count": int(group["H4_Transition_Label"].nunique()),
                "Distinct_Context_Profile_Count": len(group),
                "Research_Ready_Context_Count": ready_count,
                "Low_Or_Insufficient_Context_Count": low_count,
                "D1_Context_Adequacy_Class": adequacy_class,
                "D1_Context_Diagnostic": _diagnostic(adequacy_class),
            }
        )
    return pd.DataFrame(rows, columns=D1_CONTEXT_INVENTORY_COLUMNS)


def classify_d1_context_adequacy(ready_count: int, low_count: int, profile_count: int, row_count: int) -> str:
    if profile_count <= 0 or row_count <= 0:
        return "D1_CONTEXT_INPUT_LIMITED"
    if ready_count > 0 and low_count == 0:
        return "D1_CONTEXT_ADEQUATE_FOR_RESEARCH"
    if ready_count > 0:
        return "D1_CONTEXT_PARTIALLY_ADEQUATE"
    if low_count == profile_count and profile_count >= 5:
        return "D1_CONTEXT_OVER_FRAGMENTED"
    return "D1_CONTEXT_SAMPLE_CONSTRAINED"


def _diagnostic(adequacy_class: str) -> str:
    if adequacy_class == "D1_CONTEXT_ADEQUATE_FOR_RESEARCH":
        return "D1 context has research-ready H4 transition profiles."
    if adequacy_class == "D1_CONTEXT_PARTIALLY_ADEQUATE":
        return "D1 context has mixed research-ready and sample-constrained profiles."
    if adequacy_class == "D1_CONTEXT_OVER_FRAGMENTED":
        return "D1 context fragments H4 transition profiles into constrained samples."
    if adequacy_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "D1 context sample is constrained for later outcome research."
    return "D1 context input is missing or empty."
