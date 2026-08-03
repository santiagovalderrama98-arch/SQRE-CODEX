"""Configuration for H4/D1 synchronized historical data preparation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4D1SynchronizedDataPreparationConfig:
    """Runtime configuration for Phase 7.5.14D."""

    symbol: str = "EURUSD"
    h4_input: Path = Path("data/raw/EURUSD_H4.csv")
    output_dir: Path = Path("data/research/h4_d1_synchronized_data_preparation")
    report_path: Path = Path("data/research/h4_d1_synchronized_data_preparation/h4_d1_synchronized_data_report.txt")
    start_date: str = ""
    end_date: str = ""
    timezone: str = "UTC"
    minimum_h4_continuity_ratio: float = 0.90
    minimum_d1_h4_candle_count: int = 4
    expected_h4_candles_per_d1: int = 6
    build_d1_from_h4: bool = True
    allow_download: bool = False
    provider: str | None = None
    validation_config: Path = Path("configs/validation/h4_d1_structural_research_validation.yaml")
    validation_summary: Path = Path("data/validation/h4_d1_structural_research/h4_d1_validation_summary.csv")
