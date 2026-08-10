"""Models and small helpers for reference stability validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ReferenceStabilitySourceInventoryRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    diagnostic: str


@dataclass(frozen=True)
class ReferenceStabilityValidationSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    reference_count: int
    core_reference_count: int
    supporting_reference_count: int
    query_result_count: int
    dashboard_reference_card_count: int
    stable_horizon_count: int
    partial_horizon_count: int
    unstable_horizon_count: int
    stable_granularity_count: int
    partial_granularity_count: int
    fragmented_granularity_count: int
    stable_sample_group_count: int
    usable_sample_group_count: int
    low_sample_group_count: int
    stable_dispersion_group_count: int
    usable_dispersion_group_count: int
    high_dispersion_group_count: int
    stable_match_level_count: int
    fallback_dependent_match_level_count: int
    scope_safety_status: str
    dominant_reference_stability_readiness_class: str
    reference_stability_readiness_flag: str
    reference_stability_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ReferenceStabilityValidationResult:
    output_dir: Path
    report_path: Path
    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    source_inventory: list[ReferenceStabilitySourceInventoryRow] = field(default_factory=list)
    reference_population_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    granularity_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_adequacy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    dispersion_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    directional_consistency_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    match_level_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    dashboard_reference_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_stability_scorecard: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ReferenceStabilityValidationSummary | None = None


def resolve_column(frame: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    """Return the first matching column, case-insensitively."""

    normalized = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = normalized.get(str(alias).strip().lower())
        if column is not None:
            return column
    return None


def series(frame: pd.DataFrame, aliases: Iterable[str], default: object = "") -> pd.Series:
    column = resolve_column(frame, aliases)
    if column is None:
        return pd.Series([default] * len(frame), index=frame.index)
    return frame[column]


def numeric_series(frame: pd.DataFrame, aliases: Iterable[str]) -> pd.Series:
    return pd.to_numeric(series(frame, aliases, 0), errors="coerce").fillna(0)


def text_series(frame: pd.DataFrame, aliases: Iterable[str]) -> pd.Series:
    return series(frame, aliases, "").astype(str).str.strip()


def value_count(frame: pd.DataFrame, aliases: Iterable[str], value: str) -> int:
    values = text_series(frame, aliases).str.upper()
    return int((values == value.upper()).sum())


def safe_mean(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    return round(float(pd.to_numeric(values, errors="coerce").fillna(0).mean()), 4)


def safe_median(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    return round(float(pd.to_numeric(values, errors="coerce").fillna(0).median()), 4)


def tier_counts(frame: pd.DataFrame, aliases: Iterable[str] = ("Reference_Tier", "Matched_Reference_Tier")) -> tuple[int, int, int]:
    values = text_series(frame, aliases).str.upper()
    core = int(values.isin({"CORE_RESEARCH_REFERENCE", "CORE_REFERENCE"}).sum())
    supporting = int(values.isin({"SUPPORTING_RESEARCH_REFERENCE", "SUPPORTING_REFERENCE"}).sum())
    watchlist = int(values.isin({"WATCHLIST_RESEARCH_REFERENCE", "WATCHLIST_REFERENCE"}).sum())
    return core, supporting, watchlist
