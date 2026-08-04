"""D1 context sample adequacy review."""

from __future__ import annotations

import pandas as pd


D1_CONTEXT_SAMPLE_ADEQUACY_COLUMNS = [
    "D1_Context_ID",
    "D1_Market_State",
    "D1_Regime_Label",
    "Aligned_H4_Transition_Row_Count",
    "Distinct_H4_Transition_Count",
    "Research_Ready_Context_Count",
    "Low_Or_Insufficient_Context_Count",
    "Context_Research_Ready_Ratio",
    "D1_Context_Adequacy_Class",
    "Adequacy_Diagnostic",
]


def build_d1_context_sample_adequacy_review(d1_context_inventory: pd.DataFrame) -> pd.DataFrame:
    if d1_context_inventory.empty:
        return pd.DataFrame(columns=D1_CONTEXT_SAMPLE_ADEQUACY_COLUMNS)
    rows = []
    for _, row in d1_context_inventory.iterrows():
        ready = int(row["Research_Ready_Context_Count"])
        low = int(row["Low_Or_Insufficient_Context_Count"])
        total_profiles = ready + low
        ratio = round(ready / total_profiles, 6) if total_profiles else 0.0
        rows.append(
            {
                "D1_Context_ID": row["D1_Context_ID"],
                "D1_Market_State": row["D1_Market_State"],
                "D1_Regime_Label": row["D1_Regime_Label"],
                "Aligned_H4_Transition_Row_Count": int(row["Aligned_H4_Transition_Row_Count"]),
                "Distinct_H4_Transition_Count": int(row["Distinct_H4_Transition_Count"]),
                "Research_Ready_Context_Count": ready,
                "Low_Or_Insufficient_Context_Count": low,
                "Context_Research_Ready_Ratio": ratio,
                "D1_Context_Adequacy_Class": row["D1_Context_Adequacy_Class"],
                "Adequacy_Diagnostic": _diagnostic(str(row["D1_Context_Adequacy_Class"])),
            }
        )
    return pd.DataFrame(rows, columns=D1_CONTEXT_SAMPLE_ADEQUACY_COLUMNS)


def _diagnostic(adequacy_class: str) -> str:
    if adequacy_class == "D1_CONTEXT_ADEQUATE_FOR_RESEARCH":
        return "D1 context has enough research-ready profiles for later outcome research."
    if adequacy_class == "D1_CONTEXT_PARTIALLY_ADEQUATE":
        return "D1 context contains a mix of research-ready and constrained profiles."
    if adequacy_class == "D1_CONTEXT_OVER_FRAGMENTED":
        return "D1 context is over-fragmenting current H4 transition samples."
    if adequacy_class == "D1_CONTEXT_SAMPLE_CONSTRAINED":
        return "D1 context has constrained profile samples."
    return "D1 context sample input is limited."
