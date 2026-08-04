"""Configuration for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4D1ForwardOutcomeInterpretationReviewConfig:
    forward_outcome_dir: Path = Path("data/research/h4_d1_aligned_forward_outcome_research")
    contextual_transition_dir: Path = Path("data/research/h4_d1_same_time_contextual_transition_review")
    output_dir: Path = Path("data/research/h4_d1_forward_outcome_interpretation_review")
    report_path: Path = Path(
        "data/research/h4_d1_forward_outcome_interpretation_review/"
        "h4_d1_forward_outcome_interpretation_review_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_interpretation_sample_size: int = 20
    minimum_moderate_sample_size: int = 10
    directional_imbalance_threshold: float = 0.60
    strong_directional_imbalance_threshold: float = 0.70
    high_dispersion_threshold_pips: float = 40.0
    extreme_dispersion_threshold_pips: float = 80.0
