from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest

from sqre.data_acquisition.providers.mt5_provider import MT5Provider


class FakeMT5:
    TIMEFRAME_M1 = 1
    TIMEFRAME_M5 = 5
    TIMEFRAME_M15 = 15
    TIMEFRAME_M30 = 30
    TIMEFRAME_H1 = 60
    TIMEFRAME_H4 = 240
    TIMEFRAME_D1 = 1440

    def __init__(self, initialize_result=True, symbol_visible=True, symbol_select_result=True, rates=None):
        self.initialize_result = initialize_result
        self.symbol_visible = symbol_visible
        self.symbol_select_result = symbol_select_result
        self.rates = rates
        self.shutdown_called = False
        self.copy_call = None

    def initialize(self):
        return self.initialize_result

    def shutdown(self):
        self.shutdown_called = True

    def last_error(self):
        return (1, "terminal unavailable")

    def symbol_info(self, symbol):
        return SimpleNamespace(visible=self.symbol_visible)

    def symbol_select(self, symbol, enabled):
        return self.symbol_select_result

    def copy_rates_range(self, symbol, timeframe, start, end):
        self.copy_call = (symbol, timeframe, start, end)
        return self.rates


def test_supports_symbols_with_mapped_timeframes():
    provider = MT5Provider(mt5_module=FakeMT5())

    assert provider.supports("EURUSD", "M5")
    assert provider.supports("GBPJPY", "H4")
    assert not provider.supports("EURUSD", "M2")
    assert not provider.supports("", "M5")


def test_download_maps_timeframe_and_normalizes_tick_volume():
    fake_mt5 = FakeMT5(
        rates=[
            {
                "time": 1577836800,
                "open": 1.1,
                "high": 1.2,
                "low": 1.0,
                "close": 1.15,
                "tick_volume": 123,
            }
        ]
    )
    provider = MT5Provider(mt5_module=fake_mt5)

    raw = provider.download("EURUSD", "M5", date(2020, 1, 1), date(2020, 1, 31))
    normalized = provider.normalize(raw)

    assert fake_mt5.copy_call is not None
    symbol, timeframe, start, end = fake_mt5.copy_call
    assert symbol == "EURUSD"
    assert timeframe == fake_mt5.TIMEFRAME_M5
    assert start == datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert end.date() == date(2020, 1, 31)
    assert fake_mt5.shutdown_called is True
    assert list(normalized.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert normalized.iloc[0]["Volume"] == 123


def test_download_fails_when_metatrader5_package_is_missing(monkeypatch):
    def fake_import_module(name):
        raise ImportError("missing package")

    monkeypatch.setattr("sqre.data_acquisition.providers.mt5_provider.importlib.import_module", fake_import_module)
    provider = MT5Provider()

    with pytest.raises(RuntimeError, match="MetaTrader5 Python package is not installed"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))


def test_download_fails_when_terminal_initialize_fails():
    provider = MT5Provider(mt5_module=FakeMT5(initialize_result=False))

    with pytest.raises(RuntimeError, match="initialization failed"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))


def test_download_fails_when_symbol_cannot_be_selected():
    provider = MT5Provider(mt5_module=FakeMT5(symbol_visible=False, symbol_select_result=False))

    with pytest.raises(RuntimeError, match="could not be selected"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))


def test_download_fails_when_no_data_is_returned():
    provider = MT5Provider(mt5_module=FakeMT5(rates=[]))

    with pytest.raises(RuntimeError, match="no data"):
        provider.download("EURUSD", "M1", date(2020, 1, 1), date(2020, 1, 2))
