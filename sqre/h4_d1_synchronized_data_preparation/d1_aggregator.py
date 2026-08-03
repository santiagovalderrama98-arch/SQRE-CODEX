"""D1 OHLC aggregation from normalized H4 candles."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig


def build_d1_from_h4(h4_frame: pd.DataFrame, config: H4D1SynchronizedDataPreparationConfig) -> pd.DataFrame:
    columns = [
        "Date",
        "D1_Period_Start",
        "D1_Period_End",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Symbol",
        "Timeframe",
        "H4_Candle_Count",
        "Expected_H4_Candle_Count",
        "D1_Candle_Quality_Class",
        "D1_Aggregation_Diagnostic",
    ]
    if h4_frame.empty or not config.build_d1_from_h4:
        return pd.DataFrame(columns=columns)
    frame = h4_frame.copy()
    frame["_DateTime"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.dropna(subset=["_DateTime"]).sort_values("_DateTime")
    frame["_D1Date"] = frame["_DateTime"].dt.date.astype(str)
    rows: list[dict[str, object]] = []
    for date_value, group in frame.groupby("_D1Date", sort=True):
        group = group.sort_values("_DateTime")
        count = len(group)
        rows.append(
            {
                "Date": date_value,
                "D1_Period_Start": group["_DateTime"].iloc[0].strftime("%Y-%m-%d %H:%M:%S"),
                "D1_Period_End": group["_DateTime"].iloc[-1].strftime("%Y-%m-%d %H:%M:%S"),
                "Open": group["Open"].iloc[0],
                "High": group["High"].max(),
                "Low": group["Low"].min(),
                "Close": group["Close"].iloc[-1],
                "Volume": group["Volume"].sum(),
                "Symbol": config.symbol,
                "Timeframe": "D1",
                "H4_Candle_Count": count,
                "Expected_H4_Candle_Count": config.expected_h4_candles_per_d1,
                "D1_Candle_Quality_Class": _quality(count, config),
                "D1_Aggregation_Diagnostic": _diagnostic(count, config),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def _quality(count: int, config: H4D1SynchronizedDataPreparationConfig) -> str:
    if count >= config.expected_h4_candles_per_d1:
        return "FULL_H4_DERIVED_D1_CANDLE"
    if count >= config.minimum_d1_h4_candle_count:
        return "PARTIAL_H4_DERIVED_D1_CANDLE"
    if count > 0:
        return "LOW_COVERAGE_H4_DERIVED_D1_CANDLE"
    return "INVALID_H4_DERIVED_D1_CANDLE"


def _diagnostic(count: int, config: H4D1SynchronizedDataPreparationConfig) -> str:
    if count >= config.expected_h4_candles_per_d1:
        return "D1 candle was derived from expected H4 candle coverage."
    if count >= config.minimum_d1_h4_candle_count:
        return "D1 candle was derived from partial H4 candle coverage."
    if count > 0:
        return "D1 candle has low H4 candle coverage."
    return "D1 candle could not be constructed from H4 candles."
