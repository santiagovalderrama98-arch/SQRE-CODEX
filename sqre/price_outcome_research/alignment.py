"""OHLC alignment utilities for price outcome research."""

from __future__ import annotations

from datetime import datetime

from sqre.price_outcome_research.models import OHLCCandle


def find_reference_candle(candles: list[OHLCCandle], reference_time: datetime) -> int | None:
    for index, candle in enumerate(candles):
        if candle.date >= reference_time:
            return index
    return None


def get_forward_window(
    candles: list[OHLCCandle],
    reference_index: int,
    forward_window_candles: int,
) -> tuple[list[OHLCCandle], bool]:
    start_index = reference_index + 1
    end_index = start_index + forward_window_candles
    forward_candles = candles[start_index:end_index]
    return forward_candles, len(forward_candles) == forward_window_candles
