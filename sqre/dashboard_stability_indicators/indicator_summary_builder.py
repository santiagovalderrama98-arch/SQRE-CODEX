"""Aggregate indicator summary helpers."""

from __future__ import annotations

import pandas as pd


def count_indicator(frame: pd.DataFrame, value: str) -> int:
    if frame.empty or "Dashboard_Stability_Indicator_Class" not in frame.columns:
        return 0
    return int((frame["Dashboard_Stability_Indicator_Class"].astype(str) == value).sum())


def count_severity(frame: pd.DataFrame, value: str) -> int:
    if frame.empty or "Dashboard_Stability_Severity_Class" not in frame.columns:
        return 0
    return int((frame["Dashboard_Stability_Severity_Class"].astype(str) == value).sum())


def count_reference_warning(cards: pd.DataFrame, needle: str) -> int:
    if cards.empty:
        return 0
    text = (
        cards.get("Primary_Stability_Warning", pd.Series([""] * len(cards))).astype(str)
        + " "
        + cards.get("Secondary_Stability_Warning", pd.Series([""] * len(cards))).astype(str)
    ).str.upper()
    return int(text.str.contains(needle.upper(), regex=False).sum())
