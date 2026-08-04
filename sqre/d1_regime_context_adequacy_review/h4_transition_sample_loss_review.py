"""Review H4 transition sample loss after D1 context segmentation."""

from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig


SAMPLE_LOSS_COLUMNS = [
    "H4_Transition_Label",
    "Transition_Total_Count",
    "Minimum_Transition_Sample_Size",
    "Raw_Transition_Sample_Adequacy",
    "Research_Ready_Context_Count",
    "Context_Profile_Count",
    "Context_Profile_Ready_Ratio",
    "Low_Or_Insufficient_Context_Count",
    "Transition_Sample_Loss_Class",
    "Sample_Loss_Diagnostic",
]


def build_sample_loss_review(
    profiles: pd.DataFrame,
    config: D1RegimeContextAdequacyReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=SAMPLE_LOSS_COLUMNS)
    rows = []
    for transition_label, group in profiles.groupby("H4_Transition_Label", dropna=False):
        total = int(group["Transition_Total_Count"].max())
        ready_count = int((group["Context_Sample_Adequacy_Class"] == "RESEARCH_READY_CONTEXT_SAMPLE").sum())
        profile_count = len(group)
        low_count = int(
            group["Context_Sample_Adequacy_Class"].isin(["LOW_CONTEXT_SAMPLE", "INSUFFICIENT_CONTEXT_SAMPLE"]).sum()
        )
        ready_ratio = round(ready_count / profile_count, 6) if profile_count else 0.0
        raw_class = classify_raw_transition_sample(total, config)
        loss_class = classify_sample_loss(raw_class, ready_ratio, low_count, profile_count)
        rows.append(
            {
                "H4_Transition_Label": transition_label,
                "Transition_Total_Count": total,
                "Minimum_Transition_Sample_Size": config.minimum_transition_sample_size,
                "Raw_Transition_Sample_Adequacy": raw_class,
                "Research_Ready_Context_Count": ready_count,
                "Context_Profile_Count": profile_count,
                "Context_Profile_Ready_Ratio": ready_ratio,
                "Low_Or_Insufficient_Context_Count": low_count,
                "Transition_Sample_Loss_Class": loss_class,
                "Sample_Loss_Diagnostic": _diagnostic(loss_class),
            }
        )
    return pd.DataFrame(rows, columns=SAMPLE_LOSS_COLUMNS)


def classify_raw_transition_sample(total: int, config: D1RegimeContextAdequacyReviewConfig) -> str:
    if total >= config.minimum_transition_sample_size:
        return "RAW_TRANSITION_SAMPLE_ADEQUATE"
    if total >= max(1, config.minimum_transition_sample_size // 2):
        return "RAW_TRANSITION_SAMPLE_MODERATE"
    if total > 0:
        return "RAW_TRANSITION_SAMPLE_LOW"
    return "RAW_TRANSITION_SAMPLE_INSUFFICIENT"


def classify_sample_loss(raw_class: str, ready_ratio: float, low_count: int, profile_count: int) -> str:
    if profile_count <= 0:
        return "INPUT_MISSING"
    if raw_class == "RAW_TRANSITION_SAMPLE_ADEQUATE" and ready_ratio == 0 and low_count > 0:
        return "EXTREME_SAMPLE_LOSS"
    if ready_ratio < 0.25 and low_count > 0:
        return "HIGH_SAMPLE_LOSS"
    if ready_ratio < 0.50 and low_count > 0:
        return "MODERATE_SAMPLE_LOSS"
    return "LOW_SAMPLE_LOSS"


def _diagnostic(loss_class: str) -> str:
    if loss_class == "LOW_SAMPLE_LOSS":
        return "D1 context segmentation preserves enough context profiles."
    if loss_class == "MODERATE_SAMPLE_LOSS":
        return "D1 context segmentation reduces context profile readiness."
    if loss_class == "HIGH_SAMPLE_LOSS":
        return "D1 context segmentation substantially reduces context profile readiness."
    if loss_class == "EXTREME_SAMPLE_LOSS":
        return "Raw H4 transition sample becomes constrained after D1 context segmentation."
    return "Sample loss input is missing."
