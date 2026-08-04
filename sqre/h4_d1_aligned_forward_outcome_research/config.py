"""Configuration for H4/D1 aligned forward outcome research."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class H4D1AlignedForwardOutcomeResearchConfig:
    same_time_alignment_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    synchronized_data_dir: Path = Path("data/research/h4_d1_synchronized_data_preparation")
    contextual_transition_dir: Path = Path("data/research/h4_d1_same_time_contextual_transition_review")
    output_dir: Path = Path("data/research/h4_d1_aligned_forward_outcome_research")
    report_path: Path = Path(
        "data/research/h4_d1_aligned_forward_outcome_research/"
        "h4_d1_aligned_forward_outcome_research_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    forward_horizons: tuple[int, ...] = field(default_factory=lambda: (1, 2, 3, 6, 12))
    minimum_outcome_sample_size: int = 20
    minimum_context_outcome_sample_size: int = 10
    pip_size: float = 0.0001


def parse_forward_horizons(value: str) -> tuple[int, ...]:
    horizons = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not horizons:
        raise ValueError("At least one forward horizon is required.")
    if any(horizon <= 0 for horizon in horizons):
        raise ValueError("Forward horizons must be positive integers.")
    return horizons
