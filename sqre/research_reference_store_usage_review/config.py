"""Configuration for Research Reference Store Usage Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ResearchReferenceStoreUsageReviewConfig:
    reference_store_dir: Path = Path("data/research/research_reference_store_design")
    interpretation_dir: Path = Path("data/research/h4_d1_forward_outcome_interpretation_review")
    same_time_alignment_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    output_dir: Path = Path("data/research/research_reference_store_usage_review")
    report_path: Path = Path(
        "data/research/research_reference_store_usage_review/research_reference_store_usage_review_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    preferred_horizons: list[int] = field(default_factory=lambda: [1, 2, 3, 6, 12])
    minimum_reference_sample_size: int = 10
    minimum_core_reference_sample_size: int = 20
    maximum_reference_dispersion_pips: float = 80.0
    maximum_scenarios: int = 500
