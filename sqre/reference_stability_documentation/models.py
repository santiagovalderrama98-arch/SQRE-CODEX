"""Models and helpers for reference stability documentation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig


@dataclass(frozen=True)
class ReferenceStabilityDocumentationSourceRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    diagnostic: str


@dataclass(frozen=True)
class ReferenceStabilityDocumentationSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    stability_dimension_count: int
    documented_stable_evidence_count: int
    documented_partial_evidence_count: int
    documented_constrained_evidence_count: int
    documented_unstable_evidence_count: int
    safe_for_manual_research_review_count: int
    use_with_stability_warnings_count: int
    documentation_only_count: int
    dashboard_guide_element_count: int
    limitation_count: int
    follow_up_count: int
    high_priority_follow_up_count: int
    medium_priority_follow_up_count: int
    low_priority_follow_up_count: int
    documentation_scope_safety_class: str
    scope_warning_count: int
    scope_violation_count: int
    reference_stability_documentation_readiness_class: str
    reference_stability_documentation_readiness_flag: str
    reference_stability_documentation_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ReferenceStabilityDocumentationResult:
    output_dir: Path
    report_path: Path
    markdown_path: Path
    config: ReferenceStabilityDocumentationConfig | None = None
    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    texts: dict[str, str] = field(default_factory=dict)
    source_inventory: list[ReferenceStabilityDocumentationSourceRow] = field(default_factory=list)
    interpretation_guide: pd.DataFrame = field(default_factory=pd.DataFrame)
    evidence_usage_policy: pd.DataFrame = field(default_factory=pd.DataFrame)
    dashboard_reading_guide: pd.DataFrame = field(default_factory=pd.DataFrame)
    limitations_documentation: pd.DataFrame = field(default_factory=pd.DataFrame)
    follow_up_plan: pd.DataFrame = field(default_factory=pd.DataFrame)
    scope_safety_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ReferenceStabilityDocumentationSummary | None = None


def resolve_column(frame: pd.DataFrame, aliases: Iterable[str]) -> str | None:
    """Return the first matching column, case-insensitively."""

    normalized = {str(column).strip().lower(): str(column) for column in frame.columns}
    for alias in aliases:
        column = normalized.get(str(alias).strip().lower())
        if column is not None:
            return column
    return None


def text_series(frame: pd.DataFrame, aliases: Iterable[str], default: str = "") -> pd.Series:
    column = resolve_column(frame, aliases)
    if column is None:
        return pd.Series([default] * len(frame), index=frame.index)
    return frame[column].astype(str).str.strip()


def numeric_value(frame: pd.DataFrame, aliases: Iterable[str], default: int = 0) -> int:
    column = resolve_column(frame, aliases)
    if frame.empty or column is None:
        return default
    value = pd.to_numeric(frame[column], errors="coerce").fillna(default).iloc[0]
    return int(value)


def class_count(frame: pd.DataFrame, column: str, value: str) -> int:
    if frame.empty or column not in frame.columns:
        return 0
    return int((frame[column].astype(str).str.upper() == value.upper()).sum())


def contains_any(text: str, needles: Iterable[str]) -> bool:
    normalized = str(text).upper()
    return any(needle.upper() in normalized for needle in needles)
