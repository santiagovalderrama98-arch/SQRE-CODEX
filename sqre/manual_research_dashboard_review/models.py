"""Models for the SQRE manual research dashboard review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ReviewSourceInventoryRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    diagnostic: str


@dataclass(frozen=True)
class ManualDashboardReviewSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    dashboard_source_row_count: int
    panel_completeness_ready_count: int
    panel_completeness_partial_count: int
    panel_completeness_missing_count: int
    high_readability_panel_count: int
    moderate_readability_panel_count: int
    low_readability_panel_count: int
    core_field_count: int
    supporting_field_count: int
    diagnostic_field_count: int
    redundant_or_low_use_field_count: int
    scope_safety_class: str
    scope_warning_count: int
    scope_violation_count: int
    recommendation_count: int
    high_priority_recommendation_count: int
    medium_priority_recommendation_count: int
    low_priority_recommendation_count: int
    dashboard_usability_readiness_class: str
    dashboard_usability_readiness_flag: str
    dashboard_usability_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ManualResearchDashboardReviewResult:
    output_dir: Path
    report_path: Path
    html_path: Path
    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    texts: dict[str, str] = field(default_factory=dict)
    source_inventory: list[ReviewSourceInventoryRow] = field(default_factory=list)
    panel_completeness: pd.DataFrame = field(default_factory=pd.DataFrame)
    panel_readability: pd.DataFrame = field(default_factory=pd.DataFrame)
    field_usefulness: pd.DataFrame = field(default_factory=pd.DataFrame)
    redundancy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    scope_safety: pd.DataFrame = field(default_factory=pd.DataFrame)
    refinement_recommendations: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ManualDashboardReviewSummary | None = None
