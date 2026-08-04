"""Validation for research query requests."""

from __future__ import annotations

import pandas as pd


def validate_query_request(row: pd.Series) -> tuple[str, str]:
    if row.get("Research_Query_Mode") == "INPUT_MISSING":
        return "INPUT_MISSING", "No query source inputs were available."
    label = str(row.get("H4_Transition_Label", "")).strip()
    if not label or label == "INPUT_MISSING":
        return "INVALID_RESEARCH_QUERY", "H4_Transition_Label is required for a research query."
    if not row.get("Requested_Forward_Horizon_H4_Candles"):
        return "PARTIAL_RESEARCH_QUERY", "Research query has H4 transition context but no requested forward horizon."
    return "VALID_RESEARCH_QUERY", "Research query is valid for descriptive lookup."
