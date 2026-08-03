"""Configuration for H4 timestamped state/transition output generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4TimestampedStateTransitionConfig:
    """Runtime configuration for Phase 7.5.14C."""

    h4_d1_validation_dir: Path = Path("data/validation/h4_d1_structural_research")
    h4_d1_structural_research_dir: Path = Path("data/research/h4_d1_structural_research")
    validation_config: Path = Path("configs/validation/h4_d1_structural_research_validation.yaml")
    output_dir: Path = Path("data/research/h4_timestamped_state_transition_outputs")
    report_path: Path = Path(
        "data/research/h4_timestamped_state_transition_outputs/h4_timestamped_state_transition_report.txt"
    )
    symbol: str = "EURUSD"
    timeframe: str = "H4"
    minimum_scenario_coverage_ratio: float = 0.80
    allow_regeneration: bool = True
