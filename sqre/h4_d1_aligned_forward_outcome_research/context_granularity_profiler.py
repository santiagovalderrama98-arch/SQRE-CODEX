"""Context granularity definitions for H4/D1 aligned outcomes."""

from __future__ import annotations


CONTEXT_GRANULARITIES = {
    "H4_TRANSITION_ONLY": ["H4_Transition_Label"],
    "H4_TRANSITION_PLUS_D1_MARKET_STATE": ["H4_Transition_Label", "D1_Market_State"],
    "H4_TRANSITION_PLUS_D1_REGIME": ["H4_Transition_Label", "D1_Regime_Label"],
    "H4_TRANSITION_PLUS_D1_STATE_AND_REGIME": [
        "H4_Transition_Label",
        "D1_Market_State",
        "D1_Regime_Label",
    ],
}


def granularity_group_columns(granularity: str) -> list[str]:
    return CONTEXT_GRANULARITIES[granularity]
