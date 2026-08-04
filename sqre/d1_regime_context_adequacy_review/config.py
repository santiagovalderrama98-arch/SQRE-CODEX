"""Configuration for D1 regime context adequacy review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class D1RegimeContextAdequacyReviewConfig:
    contextual_transition_dir: Path = Path("data/research/h4_d1_same_time_contextual_transition_review")
    same_time_alignment_dir: Path = Path("data/research/h4_d1_same_time_alignment_table")
    timestamped_state_regime_dir: Path = Path("data/research/timestamped_h4_d1_state_regime_generation")
    output_dir: Path = Path("data/research/d1_regime_context_adequacy_review")
    report_path: Path = Path(
        "data/research/d1_regime_context_adequacy_review/d1_regime_context_adequacy_review_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_context_sample_size: int = 10
    minimum_transition_sample_size: int = 20
    fragmentation_ratio_threshold: float = 0.70
    dominant_context_share_threshold: float = 0.60
