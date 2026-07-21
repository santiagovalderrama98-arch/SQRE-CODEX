"""Configuration for H4 expanded sample feasibility review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4ExpandedSampleFeasibilityConfig:
    sample_config: Path = Path("configs/validation/eurusd_expanded_historical_samples.yaml")
    expanded_validation_config: Path = Path("configs/validation/eurusd_expanded_historical_validation.yaml")
    h4_d1_validation_config: Path = Path("configs/validation/h4_d1_structural_research_validation.yaml")
    availability_csv: Path = Path("data/validation/expanded_historical_data_availability.csv")
    master_summary_csv: Path = Path("data/validation/master_historical_calibration/master_historical_summary.csv")
    expanded_summary_csv: Path = Path("data/validation/expanded_historical_consolidated/all_timeframes_expanded_summary.csv")
    h4_d1_validation_summary: Path = Path("data/validation/h4_d1_structural_research/h4_d1_validation_summary.csv")
    h4_d1_research_dir: Path = Path("data/research/h4_d1_structural_research")
    raw_data_dir: Path = Path("data/raw")
    partial_data_dir: Path = Path("data/raw/partial")
    minimum_full_coverage_ratio: float = 0.90
    minimum_partial_coverage_ratio: float = 0.50
