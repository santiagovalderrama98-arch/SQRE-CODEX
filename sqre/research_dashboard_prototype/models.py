"""Models for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DashboardSourceInventoryRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    diagnostic: str


@dataclass(frozen=True)
class ResearchDashboardSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    snapshot_mode: str
    snapshot_source: str
    research_reference_count: int
    snapshot_query_count: int
    snapshot_result_count: int
    snapshot_reference_coverage_ratio: float
    reference_card_count: int
    evidence_panel_row_count: int
    behavior_panel_row_count: int
    fallback_panel_row_count: int
    diagnostic_panel_row_count: int
    primary_snapshot_query_match_level: str
    primary_snapshot_horizon: str
    dashboard_readiness_class: str
    dashboard_readiness_flag: str
    dashboard_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ResearchDashboardPrototypeResult:
    output_dir: Path
    report_path: Path
    html_path: Path
    source_inventory: list[DashboardSourceInventoryRow] = field(default_factory=list)
    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    snapshot_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_cards: pd.DataFrame = field(default_factory=pd.DataFrame)
    evidence_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    behavior_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    fallback_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    diagnostic_panel: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ResearchDashboardSummary | None = None
