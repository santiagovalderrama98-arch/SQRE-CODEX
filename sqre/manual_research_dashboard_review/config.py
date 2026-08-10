"""Configuration for the SQRE manual research dashboard review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ManualResearchDashboardReviewConfig:
    dashboard_dir: Path = Path("data/research/research_dashboard_prototype")
    snapshot_research_dir: Path = Path("data/research/current_market_state_snapshot_research")
    query_interface_dir: Path = Path("data/research/research_query_interface_design")
    output_dir: Path = Path("data/research/manual_research_dashboard_review")
    report_path: Path = Path(
        "data/research/manual_research_dashboard_review/manual_research_dashboard_review_report.txt"
    )
    html_path: Path = Path("data/research/manual_research_dashboard_review/manual_research_dashboard_refined.html")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    maximum_reference_cards: int = 10
    maximum_fallback_rows: int = 15
    dashboard_title: str = "SQRE Manual Research Dashboard Review"
    include_field_usefulness_review: bool = True
    include_redundancy_review: bool = True
    include_scope_safety_review: bool = True
