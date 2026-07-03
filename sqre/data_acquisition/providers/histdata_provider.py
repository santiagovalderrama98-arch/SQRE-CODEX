"""HistData provider integration.

HistData direct downloads are intentionally not automated in SQRE v1.0 because
their website flow can be unstable from managed environments. The provider
therefore exposes reliable local-file normalization and a clear download error.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from sqre.data_acquisition.normalizer import DataNormalizer


class HistDataProvider:
    """Preferred SQRE v1.0 historical data provider."""

    name = "histdata"

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
            "HistData automatic download is not enabled in SQRE v1.0. "
            "Download the ZIP/CSV from HistData manually, then run: "
            "python3 scripts/ingest_histdata_file.py --file data/external/DAT_ASCII_EURUSD_M1_2020.csv "
            "--symbol EURUSD --timeframe M1"
        )

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        return self.normalizer.normalize(raw_data)

    def ingest_file(self, file_path: Path | str) -> pd.DataFrame:
        return self.normalizer.from_csv(file_path)
