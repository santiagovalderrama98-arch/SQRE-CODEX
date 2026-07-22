"""CSV helpers for H4 partial sample complementary dispersion review."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    return pd.read_csv(resolved)


def column_lookup(frame: pd.DataFrame) -> dict[str, str]:
    return {str(column).strip().lower(): str(column) for column in frame.columns}


def resolve_column(frame: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    lookup = column_lookup(frame)
    for alias in aliases:
        resolved = lookup.get(str(alias).strip().lower())
        if resolved is not None:
            return resolved
    return None


def value(row: pd.Series, aliases: Iterable[str], default: object = "") -> object:
    lookup = {str(column).strip().lower(): column for column in row.index}
    for alias in aliases:
        key = lookup.get(str(alias).strip().lower())
        if key is None:
            continue
        raw = row.get(key)
        if pd.isna(raw):
            return default
        return raw
    return default


def text_value(row: pd.Series, aliases: Iterable[str], default: str = "") -> str:
    raw = value(row, aliases, default)
    if pd.isna(raw):
        return default
    return str(raw).strip()


def number_value(row: pd.Series, aliases: Iterable[str], default: float = 0.0) -> float:
    raw = value(row, aliases, default)
    try:
        if pd.isna(raw):
            return default
        return float(raw)
    except (TypeError, ValueError):
        return default


def int_value(row: pd.Series, aliases: Iterable[str], default: int = 0) -> int:
    return int(round(number_value(row, aliases, float(default))))


def first_row(frame: pd.DataFrame) -> pd.Series | None:
    if frame.empty:
        return None
    return frame.iloc[0]


def source_status(source_name: str, source_type: str, path: Path, frame: pd.DataFrame) -> tuple[str, int, str]:
    if not path.exists():
        return "MISSING", 0, "Source file was not found."
    if frame.empty:
        return "EMPTY", 0, "Source file was found but has no data rows."
    return "LOADED", len(frame), "Source file loaded."


def most_common_text(frame: pd.DataFrame, aliases: Iterable[str], default: str = "") -> str:
    column = resolve_column(frame, aliases)
    if column is None or frame.empty:
        return default
    values = frame[column].dropna().map(lambda raw: str(raw).strip())
    if values.empty:
        return default
    return str(values.mode().iloc[0])


def mean_numeric(frame: pd.DataFrame, aliases: Iterable[str]) -> float:
    column = resolve_column(frame, aliases)
    if column is None or frame.empty:
        return 0.0
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty:
        return 0.0
    return float(values.mean())
