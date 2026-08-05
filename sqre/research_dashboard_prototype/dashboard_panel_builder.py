"""Shared panel helpers for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def first_value(frame: pd.DataFrame, columns: Iterable[str], default: object = "") -> object:
    if frame.empty:
        return default
    for column in columns:
        if column in frame.columns:
            values = frame[column].replace("", pd.NA).dropna()
            if not values.empty:
                return values.iloc[0]
    return default


def row_value(row: pd.Series, columns: Iterable[str], default: object = "") -> object:
    for column in columns:
        if column in row.index:
            value = row.get(column, default)
            if pd.notna(value) and str(value) != "":
                return value
    return default


def numeric_mean(frame: pd.DataFrame, column: str) -> float:
    if frame.empty or column not in frame.columns:
        return 0.0
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    return round(float(values.mean()), 4) if not values.empty else 0.0


def count_value(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column].astype(str) == value).sum())


def unique_count(frame: pd.DataFrame, column: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int(frame[column].replace("", pd.NA).dropna().astype(str).nunique())


def panel_status(frame: pd.DataFrame, missing_required: bool = False) -> str:
    if missing_required:
        return "INPUT_MISSING"
    return "PANEL_EMPTY" if frame.empty else "PANEL_READY"


def reindex(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(frame).reindex(columns=columns)
