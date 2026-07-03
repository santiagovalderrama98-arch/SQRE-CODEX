"""Experimental Dukascopy provider placeholder."""

from __future__ import annotations

from datetime import date

import pandas as pd

from sqre.data_acquisition.normalizer import DataNormalizer


class DukascopyProvider:
    """Optional experimental provider kept behind the common interface."""

    name = "dukascopy"

    _SUPPORTED_TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "D1"}

    def __init__(self, normalizer: DataNormalizer | None = None) -> None:
        self.normalizer = normalizer or DataNormalizer()

    def supports(self, symbol: str, timeframe: str) -> bool:
        return bool(symbol.strip()) and timeframe.upper() in self._SUPPORTED_TIMEFRAMES

    def download(
        self,
        symbol: str,
        timeframe: str,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        raise RuntimeError(
            "DukascopyProvider is experimental and disabled by default because "
            "DNS/403/timeout errors are unreliable in this environment."
        )

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        return self.normalizer.normalize(raw_data)
