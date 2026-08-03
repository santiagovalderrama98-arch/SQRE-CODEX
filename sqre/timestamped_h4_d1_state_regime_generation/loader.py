"""Load synchronized H4/D1 inputs for timestamped generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def expected_input_paths(synchronized_data_dir: Path) -> dict[str, Path]:
    return {
        "h4_normalized_ohlc": synchronized_data_dir / "h4_normalized_ohlc.csv",
        "d1_from_h4_ohlc": synchronized_data_dir / "d1_from_h4_ohlc.csv",
        "h4_d1_candle_alignment_map": synchronized_data_dir / "h4_d1_candle_alignment_map.csv",
        "h4_d1_synchronized_data_summary": synchronized_data_dir / "h4_d1_synchronized_data_summary.csv",
    }


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except (EmptyDataError, ParserError):
        return pd.DataFrame()


def load_h4_ohlc(synchronized_data_dir: Path) -> pd.DataFrame:
    return _normalize_ohlc(read_optional_csv(expected_input_paths(synchronized_data_dir)["h4_normalized_ohlc"]))


def load_d1_ohlc(synchronized_data_dir: Path) -> pd.DataFrame:
    return _normalize_ohlc(read_optional_csv(expected_input_paths(synchronized_data_dir)["d1_from_h4_ohlc"]))


def load_alignment_map(synchronized_data_dir: Path) -> pd.DataFrame:
    return read_optional_csv(expected_input_paths(synchronized_data_dir)["h4_d1_candle_alignment_map"])


def load_synchronized_summary(synchronized_data_dir: Path) -> pd.DataFrame:
    return read_optional_csv(expected_input_paths(synchronized_data_dir)["h4_d1_synchronized_data_summary"])


def _normalize_ohlc(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "Symbol", "Timeframe"])
    normalized = frame.copy()
    if "Date" not in normalized.columns and "D1_Period_Start" in normalized.columns:
        normalized["Date"] = normalized["D1_Period_Start"]
    required = ["Date", "Open", "High", "Low", "Close"]
    if any(column not in normalized.columns for column in required):
        return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "Symbol", "Timeframe"])
    normalized["Date"] = pd.to_datetime(normalized["Date"], errors="coerce")
    for column in ["Open", "High", "Low", "Close"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    if "Volume" in normalized.columns:
        normalized["Volume"] = pd.to_numeric(normalized["Volume"], errors="coerce").fillna(0)
    else:
        normalized["Volume"] = 0
    normalized = normalized.dropna(subset=["Date", "Open", "High", "Low", "Close"])
    return normalized.sort_values("Date").reset_index(drop=True)
