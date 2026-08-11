"""Configuration for SQRE dashboard stability indicators."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DashboardStabilityIndicatorsConfig:
    stability_documentation_dir: Path = Path("data/research/reference_stability_documentation")
    stability_validation_dir: Path = Path("data/research/reference_stability_validation")
    dashboard_dir: Path = Path("data/research/research_dashboard_prototype")
    manual_dashboard_review_dir: Path = Path("data/research/manual_research_dashboard_review")
    output_dir: Path = Path("data/research/dashboard_stability_indicators")
    report_path: Path = Path("data/research/dashboard_stability_indicators/dashboard_stability_indicators_report.txt")
    html_path: Path = Path("data/research/dashboard_stability_indicators/dashboard_stability_indicators.html")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    dashboard_title: str = "SQRE Dashboard Stability Indicators"
    maximum_reference_cards: int = 10
    maximum_fallback_rows: int = 15
    include_stability_legend: bool = True
    include_reference_card_indicators: bool = True
    include_dashboard_warnings: bool = True
    include_scope_safety_review: bool = True
