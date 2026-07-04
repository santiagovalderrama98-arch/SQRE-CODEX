"""MetaTrader 5 provider for local automatic historical Forex downloads."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from types import ModuleType
from typing import Any

import pandas as pd

from sqre.data_acquisition.normalizer import DataNormalizer


@dataclass(frozen=True)
class MT5Request:
    symbol: str
    timeframe: str
    start: datetime
    end: datetime


class MT5Provider:
    name = "mt5"

    _TIMEFRAME_NAMES = {
        "M1": "TIMEFRAME_M1",
        "M5": "TIMEFRAME_M5",
        "M15": "TIMEFRAME_M15",
        "M30": "TIMEFRAME_M30",
        "H1": "TIMEFRAME_H1",
        "H4": "TIMEFRAME_H4",
        "D1": "TIMEFRAME_D1",
    }

    def __init__(self, *, normalizer: DataNormalizer | None = None, mt5_module: ModuleType | Any | None = None) -> None:
        self.normalizer = normalizer or DataNormalizer()
        self._mt5_module = mt5_module

    def supports(self, symbol: str, timeframe: str) -> bool:
        return bool(symbol.strip()) and timeframe.upper() in self._TIMEFRAME_NAMES

    def download(self, symbol: str, timeframe: str, start: date, end: date) -> pd.DataFrame:
        mt5 = self._load_mt5()
        request = MT5Request(
            symbol=symbol.upper(),
            timeframe=timeframe.upper(),
            start=datetime.combine(start, time.min, tzinfo=timezone.utc),
            end=datetime.combine(end, time.max, tzinfo=timezone.utc),
        )

        if not mt5.initialize():
            raise RuntimeError(f"MT5 terminal initialization failed: {self._last_error(mt5)}")

        try:
            self._ensure_symbol_available(mt5, request.symbol)
            rates = mt5.copy_rates_range(
                request.symbol,
                self._map_timeframe(mt5, request.timeframe),
                request.start,
                request.end,
            )
            if rates is None or len(rates) == 0:
                raise RuntimeError(f"MT5 returned no data for {request.symbol} {request.timeframe}")
            return self._rates_to_dataframe(rates)
        finally:
            shutdown = getattr(mt5, "shutdown", None)
            if callable(shutdown):
                shutdown()

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        return self.normalizer.normalize(raw_data)

    def _load_mt5(self) -> Any:
        if self._mt5_module is not None:
            return self._mt5_module
        try:
            return importlib.import_module("MetaTrader5")
        except ImportError as exc:
            raise RuntimeError(
                "MetaTrader5 Python package is not installed. "
                "Install it with: python3 -m pip install MetaTrader5"
            ) from exc

    def _ensure_symbol_available(self, mt5: Any, symbol: str) -> None:
        symbol_info = getattr(mt5, "symbol_info", lambda value: None)(symbol)
        if symbol_info is not None and bool(getattr(symbol_info, "visible", True)):
            return

        symbol_select = getattr(mt5, "symbol_select", None)
        if not callable(symbol_select) or not symbol_select(symbol, True):
            raise RuntimeError(f"MT5 symbol is not available or could not be selected: {symbol}")

    def _map_timeframe(self, mt5: Any, timeframe: str) -> int:
        constant_name = self._TIMEFRAME_NAMES.get(timeframe.upper())
        if constant_name is None:
            raise RuntimeError(f"MT5 does not support timeframe: {timeframe}")
        if not hasattr(mt5, constant_name):
            raise RuntimeError(f"MetaTrader5 package does not expose {constant_name}")
        return int(getattr(mt5, constant_name))

    def _rates_to_dataframe(self, rates: Any) -> pd.DataFrame:
        data = pd.DataFrame(rates)
        required = {"time", "open", "high", "low", "close"}
        missing = required - set(data.columns)
        if missing:
            raise RuntimeError(f"MT5 response is missing columns: {', '.join(sorted(missing))}")

        volume_source = "tick_volume" if "tick_volume" in data.columns else "real_volume"
        return pd.DataFrame(
            {
                "Date": pd.to_datetime(data["time"], unit="s", utc=True).dt.tz_localize(None),
                "Open": data["open"],
                "High": data["high"],
                "Low": data["low"],
                "Close": data["close"],
                "Volume": data[volume_source] if volume_source in data.columns else 0,
            }
        )

    def _last_error(self, mt5: Any) -> str:
        last_error = getattr(mt5, "last_error", None)
        if not callable(last_error):
            return "unknown error"
        return str(last_error())
