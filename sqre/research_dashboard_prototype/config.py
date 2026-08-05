"""Configuration for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResearchDashboardPrototypeConfig:
    snapshot_research_dir: Path = Path("data/research/current_market_state_snapshot_research")
    query_interface_dir: Path = Path("data/research/research_query_interface_design")
    reference_store_dir: Path = Path("data/research/research_reference_store_design")
    output_dir: Path = Path("data/research/research_dashboard_prototype")
    report_path: Path = Path("data/research/research_dashboard_prototype/research_dashboard_prototype_report.txt")
    html_path: Path = Path("data/research/research_dashboard_prototype/research_dashboard_prototype.html")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    maximum_reference_cards: int = 10
    maximum_fallback_rows: int = 25
    dashboard_title: str = "SQRE Research Dashboard Prototype"
