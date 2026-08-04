"""Build same-time H4/D1 contextual transition profiles."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)


PROFILE_COLUMNS = [
    "Context_Profile_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Context_Row_Count",
    "Context_Share_Of_Total",
    "Transition_Total_Count",
    "Context_Share_Within_Transition",
    "Context_Sample_Adequacy_Class",
    "Contextual_Review_Class",
    "Context_Diagnostic",
]


def build_contextual_transition_profiles(
    transition_alignment: pd.DataFrame,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> pd.DataFrame:
    aligned = _aligned_rows(transition_alignment)
    if aligned.empty:
        return pd.DataFrame(columns=PROFILE_COLUMNS)

    total_rows = len(aligned)
    transition_totals = aligned.groupby("H4_Transition_Label", dropna=False).size().to_dict()
    group_columns = ["H4_Transition_Label", "D1_Market_State", "D1_Regime_Label", "D1_Structure_Direction"]
    grouped = aligned.groupby(group_columns, dropna=False).size().reset_index(name="Context_Row_Count")

    rows: list[dict[str, object]] = []
    for index, row in grouped.reset_index(drop=True).iterrows():
        transition_label = str(row["H4_Transition_Label"])
        context_count = int(row["Context_Row_Count"])
        transition_total = int(transition_totals.get(transition_label, 0))
        sample_class = classify_context_sample(context_count, transition_total, config)
        rows.append(
            {
                "Context_Profile_ID": f"H4_D1_CTX_PROFILE_{index + 1:06d}",
                "Symbol": config.symbol,
                "H4_Timeframe": config.h4_timeframe,
                "D1_Timeframe": config.d1_timeframe,
                "H4_Transition_Label": transition_label,
                "D1_Market_State": row["D1_Market_State"],
                "D1_Regime_Label": row["D1_Regime_Label"],
                "D1_Structure_Direction": row["D1_Structure_Direction"],
                "Context_Row_Count": context_count,
                "Context_Share_Of_Total": round(context_count / total_rows, 6) if total_rows else 0.0,
                "Transition_Total_Count": transition_total,
                "Context_Share_Within_Transition": round(context_count / transition_total, 6)
                if transition_total
                else 0.0,
                "Context_Sample_Adequacy_Class": sample_class,
                "Contextual_Review_Class": contextual_review_class(sample_class),
                "Context_Diagnostic": _context_diagnostic(sample_class),
            }
        )
    return pd.DataFrame(rows, columns=PROFILE_COLUMNS)


def classify_context_sample(
    context_count: int,
    transition_total: int,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> str:
    if context_count <= 0:
        return "INPUT_MISSING"
    if context_count >= config.minimum_context_sample_size and transition_total >= config.minimum_transition_sample_size:
        return "RESEARCH_READY_CONTEXT_SAMPLE"
    if context_count >= config.minimum_context_sample_size:
        return "MODERATE_CONTEXT_SAMPLE"
    if context_count > 0:
        return "LOW_CONTEXT_SAMPLE"
    return "INSUFFICIENT_CONTEXT_SAMPLE"


def contextual_review_class(sample_class: str) -> str:
    return {
        "RESEARCH_READY_CONTEXT_SAMPLE": "SAME_TIME_CONTEXT_RESEARCH_READY",
        "MODERATE_CONTEXT_SAMPLE": "SAME_TIME_CONTEXT_MODERATE_SAMPLE",
        "LOW_CONTEXT_SAMPLE": "SAME_TIME_CONTEXT_SAMPLE_CONSTRAINED",
        "INSUFFICIENT_CONTEXT_SAMPLE": "SAME_TIME_CONTEXT_SAMPLE_CONSTRAINED",
        "INPUT_MISSING": "SAME_TIME_CONTEXT_INPUT_LIMITED",
    }.get(sample_class, "SAME_TIME_CONTEXT_INPUT_LIMITED")


def _aligned_rows(transition_alignment: pd.DataFrame) -> pd.DataFrame:
    if transition_alignment.empty:
        return pd.DataFrame()
    frame = transition_alignment.copy()
    for column in ["H4_Transition_Label", "D1_Market_State", "D1_Regime_Label", "D1_Structure_Direction"]:
        if column not in frame.columns:
            frame[column] = ""
        frame[column] = frame[column].fillna("").astype(str)
    method = frame.get("Alignment_Method", "").astype(str) if "Alignment_Method" in frame.columns else ""
    has_context = frame["D1_Market_State"].str.len().gt(0) | frame["D1_Regime_Label"].str.len().gt(0)
    if isinstance(method, str):
        return frame[has_context].copy()
    return frame[has_context & ~method.str.contains("NO_D1_SAME_TIME_MATCH", na=False)].copy()


def _context_diagnostic(sample_class: str) -> str:
    if sample_class == "RESEARCH_READY_CONTEXT_SAMPLE":
        return "Context has sufficient same-time observations for later outcome research."
    if sample_class == "MODERATE_CONTEXT_SAMPLE":
        return "Context has moderate same-time observations and should be handled descriptively."
    if sample_class == "LOW_CONTEXT_SAMPLE":
        return "Context is sample-constrained for later outcome research."
    if sample_class == "INSUFFICIENT_CONTEXT_SAMPLE":
        return "Context has insufficient same-time observations."
    return "Same-time transition context input is missing."
