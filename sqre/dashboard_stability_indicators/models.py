"""Models and helpers for dashboard stability indicators."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig


@dataclass(frozen=True)
class DashboardStabilitySourceRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    diagnostic: str


@dataclass(frozen=True)
class DashboardStabilityIndicatorsSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    stability_dimension_count: int
    reference_card_count: int
    stable_evidence_indicator_count: int
    partial_evidence_indicator_count: int
    warning_evidence_indicator_count: int
    documentation_only_indicator_count: int
    fallback_dependent_indicator_count: int
    directionally_unstable_indicator_count: int
    moderate_stability_warning_count: int
    high_stability_warning_count: int
    scope_safety_class: str
    scope_warning_count: int
    scope_violation_count: int
    dashboard_stability_readiness_class: str
    dashboard_stability_readiness_flag: str
    dashboard_stability_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class DashboardStabilityIndicatorsResult:
    output_dir: Path
    report_path: Path
    html_path: Path
    config: DashboardStabilityIndicatorsConfig | None = None
    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    texts: dict[str, str] = field(default_factory=dict)
    source_inventory: list[DashboardStabilitySourceRow] = field(default_factory=list)
    indicator_legend: pd.DataFrame = field(default_factory=pd.DataFrame)
    indicator_map: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_card_indicators: pd.DataFrame = field(default_factory=pd.DataFrame)
    evidence_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    behavior_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    fallback_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    warning_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    scope_safety_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: DashboardStabilityIndicatorsSummary | None = None


def resolve_column(frame: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    normalized = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = normalized.get(str(alias).strip().lower())
        if column is not None:
            return column
    return None


def text_value(row: pd.Series, aliases: Iterable[str], default: str = "") -> str:
    for alias in aliases:
        if alias in row.index:
            value = row.get(alias, default)
            if pd.notna(value):
                return str(value).strip()
    return default


def text_series(frame: pd.DataFrame, aliases: Iterable[str], default: str = "") -> pd.Series:
    column = resolve_column(frame, aliases)
    if column is None:
        return pd.Series([default] * len(frame), index=frame.index)
    return frame[column].astype(str).str.strip()


def numeric_series(frame: pd.DataFrame, aliases: Iterable[str]) -> pd.Series:
    column = resolve_column(frame, aliases)
    if column is None:
        return pd.Series([0] * len(frame), index=frame.index)
    return pd.to_numeric(frame[column], errors="coerce").fillna(0)


def numeric_value(frame: pd.DataFrame, aliases: Iterable[str], default: int = 0) -> int:
    column = resolve_column(frame, aliases)
    if frame.empty or column is None:
        return default
    return int(pd.to_numeric(frame[column], errors="coerce").fillna(default).iloc[0])


def class_count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column].astype(str).str.upper() == value.upper()).sum())


def safe_mean(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return round(float(pd.to_numeric(series, errors="coerce").fillna(0).mean()), 4)
