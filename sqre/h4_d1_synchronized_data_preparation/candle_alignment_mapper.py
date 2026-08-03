"""Build H4 to D1 candle alignment rows."""

from __future__ import annotations

import pandas as pd


def build_h4_d1_alignment_map(h4_frame: pd.DataFrame, d1_frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "H4_Candle_ID",
        "Symbol",
        "H4_Timeframe",
        "D1_Timeframe",
        "H4_Timestamp",
        "H4_Date",
        "H4_Open",
        "H4_High",
        "H4_Low",
        "H4_Close",
        "H4_Volume",
        "D1_Date",
        "D1_Period_Start",
        "D1_Period_End",
        "D1_Open",
        "D1_High",
        "D1_Low",
        "D1_Close",
        "D1_Volume",
        "D1_H4_Candle_Count",
        "H4_D1_Candle_Alignment_Class",
        "Alignment_Diagnostic",
    ]
    if h4_frame.empty:
        return pd.DataFrame(columns=columns)
    d1_lookup = {str(row["Date"]): row for _, row in d1_frame.iterrows()} if not d1_frame.empty else {}
    rows: list[dict[str, object]] = []
    frame = h4_frame.copy()
    frame["_DateTime"] = pd.to_datetime(frame["Date"], errors="coerce")
    for index, row in frame.iterrows():
        h4_date = row["_DateTime"].date().isoformat() if pd.notna(row["_DateTime"]) else ""
        d1 = d1_lookup.get(h4_date)
        rows.append(_alignment_row(index + 1, row, h4_date, d1))
    return pd.DataFrame(rows, columns=columns)


def _alignment_row(index: int, h4_row, h4_date: str, d1_row) -> dict[str, object]:
    if d1_row is None:
        alignment_class = "H4_D1_CANDLE_ALIGNMENT_MISSING_D1"
        diagnostic = "No derived D1 candle was available for this H4 candle date."
        d1_values = _empty_d1_values(h4_date)
    else:
        alignment_class = _alignment_class(str(d1_row["D1_Candle_Quality_Class"]))
        diagnostic = "H4 candle mapped to derived D1 candle by date."
        d1_values = {
            "D1_Date": d1_row["Date"],
            "D1_Period_Start": d1_row["D1_Period_Start"],
            "D1_Period_End": d1_row["D1_Period_End"],
            "D1_Open": d1_row["Open"],
            "D1_High": d1_row["High"],
            "D1_Low": d1_row["Low"],
            "D1_Close": d1_row["Close"],
            "D1_Volume": d1_row["Volume"],
            "D1_H4_Candle_Count": d1_row["H4_Candle_Count"],
        }
    return {
        "H4_Candle_ID": f"H4_CANDLE_{index:06d}",
        "Symbol": h4_row.get("Symbol", ""),
        "H4_Timeframe": h4_row.get("Timeframe", "H4"),
        "D1_Timeframe": "D1",
        "H4_Timestamp": h4_row.get("Date", ""),
        "H4_Date": h4_date,
        "H4_Open": h4_row.get("Open", ""),
        "H4_High": h4_row.get("High", ""),
        "H4_Low": h4_row.get("Low", ""),
        "H4_Close": h4_row.get("Close", ""),
        "H4_Volume": h4_row.get("Volume", ""),
        **d1_values,
        "H4_D1_Candle_Alignment_Class": alignment_class,
        "Alignment_Diagnostic": diagnostic,
    }


def _alignment_class(d1_quality: str) -> str:
    if d1_quality == "FULL_H4_DERIVED_D1_CANDLE":
        return "H4_D1_CANDLE_ALIGNED"
    if d1_quality == "PARTIAL_H4_DERIVED_D1_CANDLE":
        return "H4_D1_CANDLE_ALIGNED_TO_PARTIAL_D1"
    if d1_quality == "LOW_COVERAGE_H4_DERIVED_D1_CANDLE":
        return "H4_D1_CANDLE_ALIGNMENT_LOW_COVERAGE"
    return "H4_D1_CANDLE_ALIGNMENT_MISSING_D1"


def _empty_d1_values(h4_date: str) -> dict[str, object]:
    return {
        "D1_Date": h4_date,
        "D1_Period_Start": "",
        "D1_Period_End": "",
        "D1_Open": "",
        "D1_High": "",
        "D1_Low": "",
        "D1_Close": "",
        "D1_Volume": "",
        "D1_H4_Candle_Count": 0,
    }
