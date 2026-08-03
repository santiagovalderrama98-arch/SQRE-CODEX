"""Configuration for H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4D1TemporalAlignmentFeasibilityConfig:
    h4_combined_context_dir: Path = Path("data/research/h4_transition_state_combined_context_review")
    h4_d1_structural_research_dir: Path = Path("data/research/h4_d1_structural_research")
    h4_d1_validation_dir: Path = Path("data/validation/h4_d1_structural_research")
    d1_regime_normalized_dir: Path = Path("data/research/d1_regime_normalized_research")
    d1_regime_outcome_review_dir: Path = Path("data/research/d1_regime_outcome_review")
    d1_state_deep_dive_dir: Path = Path("data/research/d1_state_outcome_deep_dive")
    output_dir: Path = Path("data/research/h4_d1_temporal_alignment_feasibility_review")
    report_path: Path = Path(
        "data/research/h4_d1_temporal_alignment_feasibility_review/"
        "h4_d1_temporal_alignment_feasibility_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    minimum_temporal_key_coverage_ratio: float = 0.80
