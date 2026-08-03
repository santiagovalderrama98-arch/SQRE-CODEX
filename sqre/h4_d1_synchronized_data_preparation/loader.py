"""OHLC loading and normalization for synchronized H4/D1 data preparation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from sqre.h4_d1_synchronized_data_preparation.models import NormalizedOhlcResult


COLUMN_ALIASES = {
    "Date": ["Date", "Timestamp", "Datetime", "Time"],
    "Open": ["Open", "open"],
    "High": ["High", "high"],
    "Low": ["Low", "low"],
    "Close": ["Close", "close"],
    "Volume": ["Volume", "volume", "TickVolume", "tick_volume"],
}


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except (EmptyDataError, ParserError):
        return pd.DataFrame()


def normalize_h4_ohlc(path: Path, symbol: str, timeframe: str = "H4") -> NormalizedOhlcResult:
    if not path.exists():
        return NormalizedOhlcResult(pd.DataFrame(columns=_output_columns()), 0, 0, 0, 0, 0, "H4 input file is missing.", False)
    raw = read_optional_csv(path)
    input_count = len(raw)
    if raw.empty:
        return NormalizedOhlcResult(pd.DataFrame(columns=_output_columns()), input_count, 0, 0, 0, 0, "H4 input file is empty.", False)

    resolved = {_target: _resolve_column(raw, aliases) for _target, aliases in COLUMN_ALIASES.items()}
    missing_required = [name for name in ["Date", "Open", "High", "Low", "Close"] if resolved[name] is None]
    if missing_required:
        diagnostic = f"Missing required OHLC columns: {','.join(missing_required)}."
        return NormalizedOhlcResult(pd.DataFrame(columns=_output_columns()), input_count, 0, 0, 0, 0, diagnostic, False)

    normalized = pd.DataFrame()
    normalized["Date"] = pd.to_datetime(raw[resolved["Date"]], errors="coerce")
    parsed = int(normalized["Date"].notna().sum())
    for column in ["Open", "High", "Low", "Close"]:
        normalized[column] = pd.to_numeric(raw[resolved[column]], errors="coerce")
    volume_missing = resolved["Volume"] is None
    normalized["Volume"] = 0 if volume_missing else pd.to_numeric(raw[resolved["Volume"]], errors="coerce").fillna(0)
    normalized = normalized.dropna(subset=["Date", "Open", "High", "Low", "Close"])

    duplicate_mask = normalized.duplicated(subset=["Date"], keep=False)
    duplicate_count = int(duplicate_mask.sum())
    conflicting_count = _conflicting_duplicate_count(normalized[duplicate_mask])
    if conflicting_count > 0:
        diagnostic = "Duplicate timestamps with conflicting OHLC values were found."
        return NormalizedOhlcResult(normalized, input_count, len(normalized), parsed, duplicate_count, conflicting_count, diagnostic, False)

    normalized = normalized.drop_duplicates(subset=["Date", "Open", "High", "Low", "Close", "Volume"])
    normalized = normalized.sort_values("Date").reset_index(drop=True)
    if not normalized.empty:
        normalized["Date"] = normalized["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    normalized["Symbol"] = symbol
    normalized["Timeframe"] = timeframe
    normalized["Source_File"] = str(path)
    diagnostic = "OHLC normalized."
    if volume_missing:
        diagnostic += " Volume was missing and filled with 0."
    normalized["Normalization_Diagnostic"] = diagnostic
    return NormalizedOhlcResult(
        normalized[_output_columns()],
        input_count,
        len(normalized),
        parsed,
        duplicate_count,
        conflicting_count,
        diagnostic,
        True,
    )


def _resolve_column(frame: pd.DataFrame, aliases: list[str]) -> str | None:
    lookup = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = lookup.get(alias.lower())
        if column is not None:
            return column
    return None


def _conflicting_duplicate_count(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    conflicts = 0
    for _, group in frame.groupby("Date"):
        if len(group[["Open", "High", "Low", "Close", "Volume"]].drop_duplicates()) > 1:
            conflicts += len(group)
    return conflicts


def _output_columns() -> list[str]:
    return [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Symbol",
        "Timeframe",
        "Source_File",
        "Normalization_Diagnostic",
    ]
