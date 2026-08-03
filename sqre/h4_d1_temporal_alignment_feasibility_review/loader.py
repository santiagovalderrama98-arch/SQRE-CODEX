"""CSV loading helpers for H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
from pandas.errors import EmptyDataError


def read_optional_csv(path: Path | str) -> pd.DataFrame:
    resolved = Path(path)
    if not resolved.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(resolved)
    except EmptyDataError:
        return pd.DataFrame()


def resolve_columns(frame: pd.DataFrame, aliases: Iterable[str]) -> list[str]:
    lookup = {str(column).strip().lower(): str(column) for column in frame.columns}
    matches: list[str] = []
    for alias in aliases:
        column = lookup.get(str(alias).strip().lower())
        if column is not None and column not in matches:
            matches.append(column)
    return matches


def joined(columns: Iterable[str]) -> str:
    return "|".join(str(column) for column in columns if str(column).strip())
