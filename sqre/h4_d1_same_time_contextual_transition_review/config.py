"""Configuration for H4/D1 same-time contextual transition review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4D1SameTimeContextualTransitionReviewConfig:
    same_time_alignment_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    timestamped_state_regime_dir: Path = Path("data/research/timestamped_h4_d1_state_regime_generation")
    output_dir: Path = Path("data/research/h4_d1_same_time_contextual_transition_review")
    report_path: Path = Path(
        "data/research/h4_d1_same_time_contextual_transition_review/"
        "h4_d1_same_time_contextual_transition_review_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_context_sample_size: int = 10
    minimum_transition_sample_size: int = 20
    concentration_ratio_threshold: float = 0.60
