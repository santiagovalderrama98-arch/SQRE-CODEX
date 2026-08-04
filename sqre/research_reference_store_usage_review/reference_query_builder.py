"""Shared CSV alias helpers for reference-store usage review."""

from __future__ import annotations

from typing import Any

import pandas as pd


def normalized_column(name: object) -> str:
    return str(name).strip().lower()


def find_column(frame: pd.DataFrame, aliases: list[str]) -> str | None:
    lookup = {normalized_column(column): str(column) for column in frame.columns}
    for alias in aliases:
        column = lookup.get(normalized_column(alias))
        if column is not None:
            return column
    return None


def row_value(row: pd.Series, aliases: list[str], default: Any = "") -> Any:
    lookup = {normalized_column(column): column for column in row.index}
    for alias in aliases:
        column = lookup.get(normalized_column(alias))
        if column is not None:
            item = row.get(column)
            if pd.notna(item):
                return item
    return default


def text_value(item: object, default: str = "") -> str:
    if pd.isna(item):
        return default
    text = str(item).strip()
    return text if text else default


def int_value(item: object, default: int = 0) -> int:
    if pd.isna(item) or item == "":
        return default
    try:
        return int(float(str(item).strip()))
    except (TypeError, ValueError):
        return default


def float_value(item: object, default: float = 0.0) -> float:
    if pd.isna(item) or item == "":
        return default
    try:
        return float(str(item).strip())
    except (TypeError, ValueError):
        return default


def same_text(left: object, right: object) -> bool:
    return text_value(left).upper() == text_value(right).upper()
