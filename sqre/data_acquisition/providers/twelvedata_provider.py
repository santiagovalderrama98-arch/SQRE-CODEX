"""Twelve Data provider for automatic historical Forex downloads."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

from sqre.data_acquisition.normalizer import DataNormalizer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TwelveDataRequest:
    symbol: str
    interval: str
    start_date: date
    end_date: date


class TwelveDataProvider:
    name = "twelvedata"

    _BASE_URL = "https://api.twelvedata.com/time_series"
    _SYMBOL_MAP = {
        "EURUSD": "EUR/USD",
        "GBPUSD": "GBP/USD",
        "AUDNZD": "AUD/NZD",
        "USDCHF": "USD/CHF",
    }
    _TIMEFRAME_MAP = {
        "M1": "1min",
        "M5": "5min",
        "M15": "15min",
        "M30": "30min",
        "H1": "1h",
        "H4": "4h",
        "D1": "1day",
    }

    def __init__(self, *, api_key: str | None = None, normalizer: DataNormalizer | None = None) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("TWELVE_DATA_API_KEY")
        self.normalizer = normalizer or DataNormalizer()

    def supports(self, symbol: str, timeframe: str) -> bool:
        return symbol.upper() in self._SYMBOL_MAP and timeframe.upper() in self._TIMEFRAME_MAP

    def download(self, symbol: str, timeframe: str, start: date, end: date) -> pd.DataFrame:
        if not self.api_key:
            raise RuntimeError("Missing TWELVE_DATA_API_KEY environment variable")

        request = TwelveDataRequest(
            symbol=self._map_symbol(symbol),
            interval=self._map_timeframe(timeframe),
            start_date=start,
            end_date=end,
        )
        payload = self._fetch_time_series(request)
        return self._payload_to_dataframe(payload)

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        return self.normalizer.normalize(raw_data)

    def _fetch_time_series(self, request: TwelveDataRequest) -> dict[str, Any]:
        params = {
            "symbol": request.symbol,
            "interval": request.interval,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "apikey": self.api_key,
            "timezone": "UTC",
            "order": "ASC",
        }
        url = f"{self._BASE_URL}?{urlencode(params)}"

        try:
            with urlopen(url, timeout=30) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 429:
                raise RuntimeError("Twelve Data API limit reached") from exc
            raise RuntimeError(f"Twelve Data HTTP error {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"Twelve Data request failed: {exc.reason}") from exc

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Twelve Data returned invalid JSON") from exc

        self._raise_for_api_error(payload)
        return payload

    def _payload_to_dataframe(self, payload: dict[str, Any]) -> pd.DataFrame:
        values = payload.get("values")
        if not values:
            raise RuntimeError("Twelve Data returned no data")

        return pd.DataFrame(
            {
                "Date": item.get("datetime"),
                "Open": item.get("open"),
                "High": item.get("high"),
                "Low": item.get("low"),
                "Close": item.get("close"),
                "Volume": item.get("volume", 0),
            }
            for item in values
        )

    def _raise_for_api_error(self, payload: dict[str, Any]) -> None:
        if payload.get("status") == "error":
            message = str(payload.get("message") or "Twelve Data provider returned an error")
            code = payload.get("code")
            if code == 429 or "limit" in message.lower():
                raise RuntimeError(f"Twelve Data API limit reached: {message}")
            raise RuntimeError(f"Twelve Data provider error: {message}")

    def _map_symbol(self, symbol: str) -> str:
        mapped = self._SYMBOL_MAP.get(symbol.upper())
        if mapped is None:
            raise RuntimeError(f"Twelve Data does not support symbol: {symbol}")
        return mapped

    def _map_timeframe(self, timeframe: str) -> str:
        mapped = self._TIMEFRAME_MAP.get(timeframe.upper())
        if mapped is None:
            raise RuntimeError(f"Twelve Data does not support timeframe: {timeframe}")
        return mapped
