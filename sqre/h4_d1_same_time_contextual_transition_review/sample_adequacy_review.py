"""Sample adequacy review for H4/D1 contextual transition profiles."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)


SAMPLE_ADEQUACY_COLUMNS = [
    "Context_Profile_ID",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Context_Row_Count",
    "Minimum_Context_Sample_Size",
    "Context_Sample_Adequacy_Class",
    "Ready_For_Outcome_Research",
    "Sample_Adequacy_Diagnostic",
]


def build_sample_adequacy_review(
    profiles: pd.DataFrame,
    config: H4D1SameTimeContextualTransitionReviewConfig,
) -> pd.DataFrame:
    if profiles.empty:
        return pd.DataFrame(columns=SAMPLE_ADEQUACY_COLUMNS)
    rows = []
    for _, row in profiles.iterrows():
        sample_class = row["Context_Sample_Adequacy_Class"]
        ready = sample_class == "RESEARCH_READY_CONTEXT_SAMPLE"
        rows.append(
            {
                "Context_Profile_ID": row["Context_Profile_ID"],
                "H4_Transition_Label": row["H4_Transition_Label"],
                "D1_Market_State": row["D1_Market_State"],
                "D1_Regime_Label": row["D1_Regime_Label"],
                "Context_Row_Count": int(row["Context_Row_Count"]),
                "Minimum_Context_Sample_Size": config.minimum_context_sample_size,
                "Context_Sample_Adequacy_Class": sample_class,
                "Ready_For_Outcome_Research": "TRUE" if ready else "FALSE",
                "Sample_Adequacy_Diagnostic": _diagnostic(sample_class),
            }
        )
    return pd.DataFrame(rows, columns=SAMPLE_ADEQUACY_COLUMNS)


def _diagnostic(sample_class: str) -> str:
    if sample_class == "RESEARCH_READY_CONTEXT_SAMPLE":
        return "Context sample meets the configured minimum for later outcome research."
    if sample_class == "MODERATE_CONTEXT_SAMPLE":
        return "Context sample is moderate and remains descriptive."
    if sample_class == "LOW_CONTEXT_SAMPLE":
        return "Context sample is below the configured minimum."
    if sample_class == "INSUFFICIENT_CONTEXT_SAMPLE":
        return "Context sample is insufficient."
    return "Context sample input is missing."
