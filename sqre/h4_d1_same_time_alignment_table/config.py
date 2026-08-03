"""Configuration for H4/D1 same-time alignment table generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4D1SameTimeAlignmentConfig:
    """Runtime configuration for Phase 7.5.14F."""

    timestamped_state_regime_dir: Path = Path("data/research/timestamped_h4_d1_state_regime_generation")
    synchronized_data_dir: Path = Path("data/research/h4_d1_synchronized_data_preparation")
    output_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    report_path: Path = Path("data/research/h4_d1_same_time_alignment_table/h4_d1_same_time_alignment_report.txt")
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_transition_alignment_ratio: float = 0.80
    minimum_state_alignment_ratio: float = 0.80
