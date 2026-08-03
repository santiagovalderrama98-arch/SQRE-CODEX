"""Timestamped H4 market state table builder."""

from __future__ import annotations

import pandas as pd

from sqre.timestamped_h4_d1_state_regime_generation.timeframe_pipeline_adapter import (
    build_timestamped_state_candidates,
)


H4_STATE_COLUMNS = [
    "H4_State_ID",
    "Symbol",
    "Timeframe",
    "State_Event_Time",
    "State_Event_Date",
    "State_Start_Time",
    "State_End_Time",
    "Market_State",
    "Structure_ID",
    "Structure_Direction",
    "Structural_Efficiency",
    "Structural_Confidence",
    "State_Confidence",
    "State_Row_Source",
    "State_Diagnostic",
]


def build_h4_state_table(frame: pd.DataFrame, *, symbol: str, timeframe: str, window_size: int = 12) -> pd.DataFrame:
    states = build_timestamped_state_candidates(
        frame,
        symbol=symbol,
        timeframe=timeframe,
        window_size=window_size,
        state_prefix="H4_STATE",
    )
    if states.empty:
        return pd.DataFrame(columns=H4_STATE_COLUMNS)
    states = states.rename(columns={"State_ID": "H4_State_ID"})
    return states.reindex(columns=H4_STATE_COLUMNS)
