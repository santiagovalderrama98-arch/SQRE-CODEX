"""Timestamped H4 state transition table builder."""

from __future__ import annotations

import pandas as pd


H4_TRANSITION_COLUMNS = [
    "H4_Transition_ID",
    "Symbol",
    "Timeframe",
    "Transition_Time",
    "Transition_Date",
    "Source_State_ID",
    "Target_State_ID",
    "Source_State",
    "Target_State",
    "Transition_Label",
    "Source_State_Time",
    "Target_State_Time",
    "Transition_Row_Source",
    "Transition_Diagnostic",
]


def build_h4_transition_table(h4_states: pd.DataFrame) -> pd.DataFrame:
    if h4_states.empty or len(h4_states) < 2 or not _required_columns_available(h4_states):
        return pd.DataFrame(columns=H4_TRANSITION_COLUMNS)
    frame = h4_states.copy()
    starts = pd.to_datetime(frame["State_Start_Time"], errors="coerce")
    ends = pd.to_datetime(frame["State_End_Time"], errors="coerce")
    if starts.isna().any() or ends.isna().any():
        return pd.DataFrame(columns=H4_TRANSITION_COLUMNS)
    if not starts.is_monotonic_increasing:
        return pd.DataFrame(columns=H4_TRANSITION_COLUMNS)
    frame["_Start"] = starts
    frame["_End"] = ends
    if frame[["_Start", "_End"]].isna().any().any():
        return pd.DataFrame(columns=H4_TRANSITION_COLUMNS)
    frame = frame.reset_index(drop=True)

    rows: list[dict[str, object]] = []
    for index, (_, source, target) in enumerate(_pairs(frame), start=1):
        transition_time = target["_Start"]
        rows.append(
            {
                "H4_Transition_ID": f"H4_TRN_{index:06d}",
                "Symbol": source["Symbol"],
                "Timeframe": source["Timeframe"],
                "Transition_Time": transition_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Transition_Date": transition_time.date().isoformat(),
                "Source_State_ID": source["H4_State_ID"],
                "Target_State_ID": target["H4_State_ID"],
                "Source_State": source["Market_State"],
                "Target_State": target["Market_State"],
                "Transition_Label": f"{source['Market_State']} -> {target['Market_State']}",
                "Source_State_Time": source["State_End_Time"],
                "Target_State_Time": target["State_Start_Time"],
                "Transition_Row_Source": "TIMESTAMPED_H4_STATE_SEQUENCE",
                "Transition_Diagnostic": "Transition row derived from ordered timestamped H4 states.",
            }
        )
    return pd.DataFrame(rows, columns=H4_TRANSITION_COLUMNS)


def _required_columns_available(frame: pd.DataFrame) -> bool:
    required = {"H4_State_ID", "Symbol", "Timeframe", "State_Start_Time", "State_End_Time", "Market_State"}
    return required.issubset(set(frame.columns))


def _pairs(frame: pd.DataFrame):
    for position in range(len(frame) - 1):
        yield position, frame.iloc[position], frame.iloc[position + 1]
