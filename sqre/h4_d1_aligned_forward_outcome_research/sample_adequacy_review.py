"""Sample adequacy review for forward outcome profiles."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.outcome_profile_builder import minimum_sample_size_for_profile


SAMPLE_ADEQUACY_REVIEW_COLUMNS = [
    "Outcome_Profile_ID",
    "Context_Granularity",
    "H4_Transition_Label",
    "D1_Market_State",
    "D1_Regime_Label",
    "Forward_Horizon_H4_Candles",
    "Outcome_Sample_Size",
    "Minimum_Required_Sample_Size",
    "Outcome_Sample_Adequacy_Class",
    "Ready_For_Later_Interpretation",
    "Sample_Adequacy_Diagnostic",
]


def build_sample_adequacy_review(
    outcome_profiles: pd.DataFrame,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> pd.DataFrame:
    if outcome_profiles.empty:
        return pd.DataFrame(columns=SAMPLE_ADEQUACY_REVIEW_COLUMNS)
    rows = []
    for _, row in outcome_profiles.iterrows():
        adequacy_class = row["Outcome_Sample_Adequacy_Class"]
        rows.append(
            {
                "Outcome_Profile_ID": row["Outcome_Profile_ID"],
                "Context_Granularity": row["Context_Granularity"],
                "H4_Transition_Label": row["H4_Transition_Label"],
                "D1_Market_State": row["D1_Market_State"],
                "D1_Regime_Label": row["D1_Regime_Label"],
                "Forward_Horizon_H4_Candles": row["Forward_Horizon_H4_Candles"],
                "Outcome_Sample_Size": row["Outcome_Sample_Size"],
                "Minimum_Required_Sample_Size": minimum_sample_size_for_profile(row["Context_Granularity"], config),
                "Outcome_Sample_Adequacy_Class": adequacy_class,
                "Ready_For_Later_Interpretation": "TRUE"
                if adequacy_class == "OUTCOME_RESEARCH_READY_SAMPLE"
                else "FALSE",
                "Sample_Adequacy_Diagnostic": _diagnostic(adequacy_class),
            }
        )
    return pd.DataFrame(rows, columns=SAMPLE_ADEQUACY_REVIEW_COLUMNS)


def _diagnostic(adequacy_class: str) -> str:
    if adequacy_class == "OUTCOME_RESEARCH_READY_SAMPLE":
        return "Profile has enough observations for later interpretation review."
    if adequacy_class == "MODERATE_OUTCOME_SAMPLE":
        return "Profile has moderate sample depth."
    if adequacy_class == "LOW_OUTCOME_SAMPLE":
        return "Profile has low sample depth."
    if adequacy_class == "INSUFFICIENT_OUTCOME_SAMPLE":
        return "Profile has insufficient sample depth."
    return "Profile input is missing."
