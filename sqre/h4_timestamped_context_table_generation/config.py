"""Configuration for H4 timestamped context table generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class H4TimestampedContextTableGenerationConfig:
    """Runtime configuration for Phase 7.5.14B."""

    h4_combined_context_dir: Path = Path("data/research/h4_transition_state_combined_context_review")
    h4_d1_validation_dir: Path = Path("data/validation/h4_d1_structural_research")
    h4_d1_structural_research_dir: Path = Path("data/research/h4_d1_structural_research")
    output_dir: Path = Path("data/research/h4_timestamped_context_table_generation")
    report_path: Path = Path(
        "data/research/h4_timestamped_context_table_generation/h4_timestamped_context_table_report.txt"
    )
    symbol: str = "EURUSD"
    timeframe: str = "H4"
    minimum_scenario_coverage_ratio: float = 0.80
    forward_windows: tuple[int, ...] = field(default_factory=lambda: (3, 6, 12))
