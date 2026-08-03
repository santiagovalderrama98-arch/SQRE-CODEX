"""Build H4 state to D1 same-time alignment rows."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_alignment_table.d1_context_index import D1ContextIndex


STATE_ALIGNMENT_COLUMNS = [
    "H4_D1_State_Alignment_ID",
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "H4_State_ID",
    "H4_State_Event_Time",
    "H4_State_Event_Date",
    "H4_Market_State",
    "D1_State_ID",
    "D1_Date",
    "D1_Period_Start",
    "D1_Period_End",
    "D1_Market_State",
    "D1_Regime_Label",
    "D1_Structure_Direction",
    "Alignment_Method",
    "Alignment_Confidence_Class",
    "Alignment_Diagnostic",
]


def build_h4_state_alignment(
    h4_states: pd.DataFrame,
    d1_index: D1ContextIndex,
    *,
    symbol: str,
    h4_timeframe: str,
    d1_timeframe: str,
) -> pd.DataFrame:
    if h4_states.empty:
        return pd.DataFrame(columns=STATE_ALIGNMENT_COLUMNS)
    rows: list[dict[str, object]] = []
    for index, (_, row) in enumerate(h4_states.iterrows(), start=1):
        timestamp = row.get("State_Event_Time", "")
        date_value = row.get("State_Event_Date", "")
        match = d1_index.match(timestamp, date_value)
        d1 = match.row or {}
        rows.append(
            {
                "H4_D1_State_Alignment_ID": f"H4_D1_STATE_ALIGN_{index:06d}",
                "Symbol": row.get("Symbol", symbol),
                "H4_Timeframe": row.get("Timeframe", h4_timeframe),
                "D1_Timeframe": d1_timeframe,
                "H4_State_ID": row.get("H4_State_ID", ""),
                "H4_State_Event_Time": _format_timestamp(timestamp),
                "H4_State_Event_Date": str(date_value) if not pd.isna(date_value) else "",
                "H4_Market_State": row.get("Market_State", ""),
                "D1_State_ID": d1.get("D1_State_ID", ""),
                "D1_Date": d1.get("D1_Date", ""),
                "D1_Period_Start": _format_timestamp(d1.get("D1_Period_Start", "")),
                "D1_Period_End": _format_timestamp(d1.get("D1_Period_End", "")),
                "D1_Market_State": d1.get("Market_State", ""),
                "D1_Regime_Label": d1.get("Regime_Label", ""),
                "D1_Structure_Direction": d1.get("Structure_Direction", ""),
                "Alignment_Method": match.alignment_method,
                "Alignment_Confidence_Class": match.alignment_confidence_class,
                "Alignment_Diagnostic": match.alignment_diagnostic,
            }
        )
    return pd.DataFrame(rows, columns=STATE_ALIGNMENT_COLUMNS)


def _format_timestamp(value: object) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "" if value is None or pd.isna(value) else str(value)
    return parsed.strftime("%Y-%m-%d %H:%M:%S")
