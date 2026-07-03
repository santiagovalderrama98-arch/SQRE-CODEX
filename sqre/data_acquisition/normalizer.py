"""Normalize provider data into the SQRE OHLCV schema."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

STANDARD_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


class DataNormalizer:
    """Converts common OHLC CSV layouts into SQRE standard format."""

    _COLUMN_ALIASES = {
        "date": "Date",
        "datetime": "Date",
        "timestamp": "Date",
        "time": "Date",
        "open": "Open",
        "o": "Open",
        "high": "High",
        "h": "High",
        "low": "Low",
        "l": "Low",
        "close": "Close",
        "c": "Close",
        "volume": "Volume",
        "vol": "Volume",
        "v": "Volume",
    }

    def from_csv(self, path: Path | str) -> pd.DataFrame:
        """Read and normalize CSV data from disk."""

        path = Path(path)
        if path.suffix.lower() == ".zip":
            return self.normalize_histdata_zip(path)
        if self._looks_like_histdata_file(path) or self._looks_like_histdata_content(path):
            return self.normalize_histdata_csv(path)
        return self.normalize(pd.read_csv(path))

    def normalize(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Normalize already-loaded tabular data."""

        if raw_data.empty:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        data = raw_data.copy()
        if self._has_standard_columns(data):
            normalized = data[STANDARD_COLUMNS].copy()
        else:
            normalized = self._normalize_generic_ohlc(data)

        normalized["Date"] = pd.to_datetime(normalized["Date"], errors="raise")
        for column in ["Open", "High", "Low", "Close", "Volume"]:
            normalized[column] = pd.to_numeric(normalized[column], errors="raise")

        normalized = normalized.sort_values("Date").drop_duplicates("Date")
        return normalized[STANDARD_COLUMNS].reset_index(drop=True)

    def normalize_histdata_csv(self, path: Path | str) -> pd.DataFrame:
        """Normalize HistData ASCII CSV files.

        Common HistData ASCII files are semicolon-delimited and contain:
        datetime;open;high;low;close;volume
        Some exports omit volume; SQRE fills missing volume with 0.
        """

        path = Path(path)
        data = self._read_histdata_table(path)
        return self._normalize_histdata_table(data)

    def normalize_histdata_zip(self, path: Path | str) -> pd.DataFrame:
        """Normalize the first CSV file inside a HistData ZIP archive."""

        path = Path(path)
        with ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError(f"No CSV file found inside ZIP: {path}")
            with archive.open(csv_names[0]) as csv_file:
                data = self._read_histdata_table(BytesIO(csv_file.read()))
        return self._normalize_histdata_table(data)

    def _normalize_histdata_table(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.shape[1] not in {5, 6}:
            raise ValueError(f"Unsupported HistData CSV shape: {data.shape}")

        if data.shape[1] == 5:
            data.columns = ["Date", "Open", "High", "Low", "Close"]
            data["Volume"] = 0
        elif data.shape[1] >= 6:
            data = data.iloc[:, :6]
            data.columns = STANDARD_COLUMNS
        else:
            raise ValueError(f"Unsupported HistData CSV shape: {data.shape}")

        return self.normalize(data)

    def _read_histdata_table(self, source: Path | BytesIO) -> pd.DataFrame:
        return pd.read_csv(source, sep=";", header=None)

    def _normalize_generic_ohlc(self, data: pd.DataFrame) -> pd.DataFrame:
        renamed: dict[str, str] = {}
        for column in data.columns:
            normalized_name = self._COLUMN_ALIASES.get(str(column).strip().lower())
            if normalized_name:
                renamed[column] = normalized_name

        data = data.rename(columns=renamed)
        missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
        if missing == ["Volume"]:
            data["Volume"] = 0
            missing = []
        if missing:
            raise ValueError(f"Missing required OHLCV columns: {', '.join(missing)}")

        return data[STANDARD_COLUMNS].copy()

    def _has_standard_columns(self, data: pd.DataFrame) -> bool:
        return all(column in data.columns for column in STANDARD_COLUMNS)

    def _looks_like_histdata_file(self, path: Path) -> bool:
        return path.name.upper().startswith("DAT_ASCII_")

    def _looks_like_histdata_content(self, path: Path) -> bool:
        try:
            first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
        except IndexError:
            return False
        return first_line.count(";") in {4, 5}
