"""Configuration for timestamped H4/D1 state and regime generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TimestampedH4D1StateRegimeGenerationConfig:
    """Runtime configuration for Phase 7.5.14E."""

    synchronized_data_dir: Path = Path("data/research/h4_d1_synchronized_data_preparation")
    output_dir: Path = Path("data/research/timestamped_h4_d1_state_regime_generation")
    report_path: Path = Path(
        "data/research/timestamped_h4_d1_state_regime_generation/timestamped_h4_d1_state_regime_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_state_count: int = 5
    minimum_transition_count: int = 5
    h4_window_size: int = 12
    d1_window_size: int = 5
