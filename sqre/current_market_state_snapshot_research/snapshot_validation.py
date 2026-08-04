"""Snapshot context validation."""

from __future__ import annotations

import pandas as pd

from sqre.research_reference_store_usage_review.reference_query_builder import text_value


def validate_snapshot_context(row: pd.Series) -> tuple[str, str]:
    source = text_value(row.get("Snapshot_Source", ""))
    transition = text_value(row.get("H4_Transition_Label", ""))
    if source == "INPUT_MISSING":
        return "INPUT_MISSING", "No snapshot source row was available."
    if not transition:
        return "INVALID_SNAPSHOT_CONTEXT", "Snapshot is missing H4 transition context."
    d1_state = text_value(row.get("D1_Market_State", ""))
    d1_regime = text_value(row.get("D1_Regime_Label", ""))
    if not d1_state or not d1_regime:
        return "PARTIAL_SNAPSHOT_CONTEXT", "Snapshot has H4 transition context but incomplete D1 context."
    return "VALID_SNAPSHOT_CONTEXT", "Snapshot has H4 transition and D1 contextual fields."
