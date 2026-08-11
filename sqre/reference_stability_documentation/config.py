"""Configuration for SQRE reference stability documentation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReferenceStabilityDocumentationConfig:
    stability_validation_dir: Path = Path("data/research/reference_stability_validation")
    dashboard_dir: Path = Path("data/research/research_dashboard_prototype")
    manual_dashboard_review_dir: Path = Path("data/research/manual_research_dashboard_review")
    output_dir: Path = Path("data/research/reference_stability_documentation")
    report_path: Path = Path(
        "data/research/reference_stability_documentation/reference_stability_documentation_report.txt"
    )
    markdown_path: Path = Path(
        "data/research/reference_stability_documentation/reference_stability_documentation.md"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    documentation_title: str = "SQRE Reference Stability Documentation"
    include_dashboard_reading_guide: bool = True
    include_follow_up_plan: bool = True
    include_scope_safety_review: bool = True
