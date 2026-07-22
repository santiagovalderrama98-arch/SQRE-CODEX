"""CSV helpers for H4 targeted partial expansion validation."""

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
        resolved = lookup.get(alias.strip().lower())
        if resolved is not None:
            return resolved
    return None


def value(row: pd.Series, aliases: Iterable[str], default: object = "") -> object:
    lookup = {str(key).strip().lower(): key for key in row.index}
    for alias in aliases:
        key = lookup.get(alias.strip().lower())
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


def truthy_series(series: pd.Series) -> pd.Series:
    return series.map(lambda raw: str(raw).strip().lower() in {"true", "1", "yes"})


def count_data_rows(path: Path | str) -> int:
    frame = read_optional_csv(path)
    return len(frame)


def mean_column(frame: pd.DataFrame, aliases: Iterable[str]) -> float:
    column = resolve_column(frame, aliases)
    if column is None or frame.empty:
        return 0.0
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty:
        return 0.0
    return float(values.mean())


def count_false_like(frame: pd.DataFrame, aliases: Iterable[str]) -> int:
    column = resolve_column(frame, aliases)
    if column is None or frame.empty:
        return 0
    values = frame[column].map(lambda raw: str(raw).strip().lower() in {"false", "0", "no", ""})
    return int(values.sum())
