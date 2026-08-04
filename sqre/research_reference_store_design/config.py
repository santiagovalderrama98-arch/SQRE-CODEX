"""Configuration for Research Reference Store Design."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResearchReferenceStoreDesignConfig:
    interpretation_dir: Path = Path("data/research/h4_d1_forward_outcome_interpretation_review")
    forward_outcome_dir: Path = Path("data/research/h4_d1_aligned_forward_outcome_research")
    output_dir: Path = Path("data/research/research_reference_store_design")
    report_path: Path = Path("data/research/research_reference_store_design/research_reference_store_design_report.txt")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_core_reference_sample_size: int = 20
    minimum_supporting_reference_sample_size: int = 10
    maximum_core_dispersion_pips: float = 40.0
    maximum_supporting_dispersion_pips: float = 80.0
    require_stable_horizon_context: bool = False
