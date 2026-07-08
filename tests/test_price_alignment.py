from __future__ import annotations

from datetime import datetime

from sqre.price_outcome_research.alignment import find_reference_candle, get_forward_window
from sqre.price_outcome_research.loader import load_ohlc
from tests.price_outcome_test_utils import write_price_outcome_inputs


def test_reference_candle_is_first_candle_at_or_after_reference_time(tmp_path) -> None:
    _, _, ohlc_path = write_price_outcome_inputs(tmp_path)
    candles = load_ohlc(ohlc_path)

    index = find_reference_candle(candles, datetime(2026, 1, 1, 1, 30))

    assert index == 2
    assert candles[index].date == datetime(2026, 1, 1, 2, 0)


def test_forward_window_starts_after_reference_and_reports_completeness(tmp_path) -> None:
    _, _, ohlc_path = write_price_outcome_inputs(tmp_path)
    candles = load_ohlc(ohlc_path)

    forward, complete = get_forward_window(candles, 1, 3)
    partial, partial_complete = get_forward_window(candles, 5, 3)

    assert [candle.date.hour for candle in forward] == [2, 3, 4]
    assert complete is True
    assert [candle.date.hour for candle in partial] == [6]
    assert partial_complete is False
    assert find_reference_candle(candles, datetime(2026, 1, 2, 0, 0)) is None
