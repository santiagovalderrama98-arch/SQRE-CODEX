"""Market data provider protocol."""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class MarketDataProvider(Protocol):
    """Interface implemented by all SQRE market data providers."""

    @property
    def name(self) -> str:
        """Provider name used by CLIs and metadata."""

    def supports(self, symbol: str, timeframe: str) -> bool:
        """Return whether this provider supports a symbol/timeframe pair."""

    def download(
        self,
        symbol: str,
        timeframe: str,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        """Download raw market data for the requested range."""

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Normalize raw provider output to SQRE standard format."""
