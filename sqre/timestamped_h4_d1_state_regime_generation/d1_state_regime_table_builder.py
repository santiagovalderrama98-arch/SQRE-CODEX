"""Timestamped D1 market state/regime table builder."""

from __future__ import annotations

import pandas as pd

from sqre.timestamped_h4_d1_state_regime_generation.timeframe_pipeline_adapter import (
    build_timestamped_state_candidates,
)


D1_STATE_COLUMNS = [
    "D1_State_ID",
    "Symbol",
    "Timeframe",
    "D1_Date",
    "D1_Period_Start",
    "D1_Period_End",
    "Market_State",
    "Regime_Label",
    "Structure_ID",
    "Structure_Direction",
    "Structural_Efficiency",
    "Structural_Confidence",
    "State_Confidence",
    "D1_State_Row_Source",
    "D1_State_Diagnostic",
]


def build_d1_state_regime_table(frame: pd.DataFrame, *, symbol: str, timeframe: str, window_size: int = 5) -> pd.DataFrame:
    states = build_timestamped_state_candidates(
        frame,
        symbol=symbol,
        timeframe=timeframe,
        window_size=window_size,
        state_prefix="D1_STATE",
    )
    if states.empty:
        return pd.DataFrame(columns=D1_STATE_COLUMNS)
    rows: list[dict[str, object]] = []
    for _, row in states.iterrows():
        rows.append(
            {
                "D1_State_ID": row["State_ID"],
                "Symbol": row["Symbol"],
                "Timeframe": row["Timeframe"],
                "D1_Date": row["State_Event_Date"],
                "D1_Period_Start": row["State_Start_Time"],
                "D1_Period_End": row["State_End_Time"],
                "Market_State": row["Market_State"],
                "Regime_Label": _regime_label(str(row["Market_State"])),
                "Structure_ID": row["Structure_ID"],
                "Structure_Direction": row["Structure_Direction"],
                "Structural_Efficiency": row["Structural_Efficiency"],
                "Structural_Confidence": row["Structural_Confidence"],
                "State_Confidence": row["State_Confidence"],
                "D1_State_Row_Source": "SYNCHRONIZED_H4_DERIVED_D1_WINDOW_ADAPTER",
                "D1_State_Diagnostic": "Timestamped D1 state/regime row derived from synchronized H4-derived D1 OHLC window.",
            }
        )
    return pd.DataFrame(rows, columns=D1_STATE_COLUMNS)


def _regime_label(market_state: str) -> str:
    if "DIRECTIONAL" in market_state:
        return "D1_DIRECTIONAL_REGIME"
    if market_state in {"COMPLEX_CONSOLIDATION", "NEUTRAL_COMPRESSION"}:
        return "D1_CONSOLIDATION_REGIME"
    if market_state == "VOLATILE_ROTATION":
        return "D1_ROTATION_REGIME"
    if market_state == "LOW_QUALITY_STRUCTURE":
        return "D1_LOW_QUALITY_REGIME"
    return "D1_UNCLASSIFIED_REGIME"
