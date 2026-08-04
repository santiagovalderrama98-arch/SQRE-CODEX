"""Calculate forward outcomes after aligned H4 transitions."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.h4_price_path_index import H4PricePathIndex


FORWARD_OUTCOME_COLUMNS = [
    "Forward_Outcome_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_Transition_ID",
    "H4_Transition_Time",
    "H4_Transition_Label",
    "H4_Source_State",
    "H4_Target_State",
    "D1_State_ID",
    "D1_Date",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Forward_Horizon_H4_Candles",
    "Anchor_Close",
    "Forward_Close",
    "Forward_Close_Change_Pips",
    "Forward_High_Excursion_Pips",
    "Forward_Low_Excursion_Pips",
    "Forward_Range_Pips",
    "Directional_Follow_Through_Class",
    "Outcome_Completeness_Class",
    "Outcome_Diagnostic",
]


def calculate_forward_outcomes(
    transition_alignment: pd.DataFrame,
    price_index: H4PricePathIndex,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> pd.DataFrame:
    if transition_alignment.empty:
        return pd.DataFrame(columns=FORWARD_OUTCOME_COLUMNS)
    rows = []
    sequence = 1
    for _, transition in transition_alignment.iterrows():
        for horizon in config.forward_horizons:
            rows.append(_calculate_row(sequence, transition, horizon, price_index, config))
            sequence += 1
    return pd.DataFrame(rows, columns=FORWARD_OUTCOME_COLUMNS)


def _calculate_row(
    sequence: int,
    transition: pd.Series,
    horizon: int,
    price_index: H4PricePathIndex,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> dict[str, object]:
    base = _base_row(sequence, transition, horizon, config)
    anchor = price_index.find_anchor(transition.get("H4_Transition_Time", ""))
    if anchor is None:
        base.update(
            {
                "Directional_Follow_Through_Class": "INSUFFICIENT_FORWARD_DATA",
                "Outcome_Completeness_Class": "MISSING_FORWARD_WINDOW",
                "Outcome_Diagnostic": "Anchor H4 candle was not found.",
            }
        )
        return base
    window = price_index.forward_window(anchor.index, horizon)
    if window.empty:
        base.update(
            {
                "Anchor_Close": anchor.close,
                "Directional_Follow_Through_Class": "INSUFFICIENT_FORWARD_DATA",
                "Outcome_Completeness_Class": "MISSING_FORWARD_WINDOW",
                "Outcome_Diagnostic": "No forward H4 candles were available.",
            }
        )
        return base
    forward_close = float(window.iloc[-1]["Close"])
    max_high = float(window["High"].max())
    min_low = float(window["Low"].min())
    close_change = _to_pips(forward_close - anchor.close, config)
    base.update(
        {
            "Anchor_Close": anchor.close,
            "Forward_Close": forward_close,
            "Forward_Close_Change_Pips": close_change,
            "Forward_High_Excursion_Pips": _to_pips(max_high - anchor.close, config),
            "Forward_Low_Excursion_Pips": _to_pips(min_low - anchor.close, config),
            "Forward_Range_Pips": _to_pips(max_high - min_low, config),
            "Directional_Follow_Through_Class": _direction_class(close_change),
            "Outcome_Completeness_Class": "COMPLETE_FORWARD_WINDOW"
            if len(window) >= horizon
            else "PARTIAL_FORWARD_WINDOW",
            "Outcome_Diagnostic": "Forward window completed."
            if len(window) >= horizon
            else "Forward window was partially available.",
        }
    )
    return base


def _base_row(
    sequence: int,
    transition: pd.Series,
    horizon: int,
    config: H4D1AlignedForwardOutcomeResearchConfig,
) -> dict[str, object]:
    return {
        "Forward_Outcome_ID": f"H4_D1_FWD_OUTCOME_{sequence:06d}",
        "Symbol": transition.get("Symbol", config.symbol),
        "H4_Timeframe": transition.get("H4_Timeframe", config.h4_timeframe),
        "D1_Timeframe": transition.get("D1_Timeframe", config.d1_timeframe),
        "H4_Transition_ID": transition.get("H4_Transition_ID", ""),
        "H4_Transition_Time": transition.get("H4_Transition_Time", ""),
        "H4_Transition_Label": transition.get("H4_Transition_Label", ""),
        "H4_Source_State": transition.get("H4_Source_State", ""),
        "H4_Target_State": transition.get("H4_Target_State", ""),
        "D1_State_ID": transition.get("D1_State_ID", ""),
        "D1_Date": transition.get("D1_Date", ""),
        "D1_Market_State": transition.get("D1_Market_State", ""),
        "D1_Regime_Label": transition.get("D1_Regime_Label", ""),
        "D1_Structure_Direction": transition.get("D1_Structure_Direction", ""),
        "Forward_Horizon_H4_Candles": horizon,
        "Anchor_Close": None,
        "Forward_Close": None,
        "Forward_Close_Change_Pips": None,
        "Forward_High_Excursion_Pips": None,
        "Forward_Low_Excursion_Pips": None,
        "Forward_Range_Pips": None,
        "Directional_Follow_Through_Class": "",
        "Outcome_Completeness_Class": "",
        "Outcome_Diagnostic": "",
    }


def _to_pips(value: float, config: H4D1AlignedForwardOutcomeResearchConfig) -> float:
    return round(value / config.pip_size, 6)


def _direction_class(close_change_pips: float) -> str:
    if close_change_pips > 0:
        return "FORWARD_UP_MOVE"
    if close_change_pips < 0:
        return "FORWARD_DOWN_MOVE"
    return "FORWARD_FLAT_MOVE"
