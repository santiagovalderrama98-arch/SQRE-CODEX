"""Configuration for SQRE reference stability validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReferenceStabilityValidationConfig:
    reference_store_dir: Path = Path("data/research/research_reference_store_design")
    query_interface_dir: Path = Path("data/research/research_query_interface_design")
    snapshot_research_dir: Path = Path("data/research/current_market_state_snapshot_research")
    dashboard_dir: Path = Path("data/research/research_dashboard_prototype")
    manual_dashboard_review_dir: Path = Path("data/research/manual_research_dashboard_review")
    output_dir: Path = Path("data/research/reference_stability_validation")
    report_path: Path = Path("data/research/reference_stability_validation/reference_stability_validation_report.txt")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_stable_sample_size: int = 20
    minimum_usable_sample_size: int = 10
    maximum_stable_dispersion_pips: float = 50.0
    maximum_usable_dispersion_pips: float = 80.0
    minimum_query_coverage_ratio: float = 0.60
    minimum_dashboard_card_count: int = 5
