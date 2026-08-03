"""Configuration for H4/D1 contextual transition review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4D1ContextualTransitionReviewConfig:
    h4_combined_context_dir: Path = Path("data/research/h4_transition_state_combined_context_review")
    d1_regime_normalized_dir: Path = Path("data/research/d1_regime_normalized_research")
    d1_regime_outcome_review_dir: Path = Path("data/research/d1_regime_outcome_review")
    d1_state_deep_dive_dir: Path = Path("data/research/d1_state_outcome_deep_dive")
    h4_d1_structural_research_dir: Path = Path("data/research/h4_d1_structural_research")
    h4_d1_validation_dir: Path = Path("data/validation/h4_d1_structural_research")
    partial_complement_dir: Path = Path("data/research/h4_partial_complementary_dispersion_review")
    partial_validation_dir: Path = Path("data/research/h4_targeted_partial_expansion_validation")
    output_dir: Path = Path("data/research/h4_d1_contextual_transition_review")
    report_path: Path = Path(
        "data/research/h4_d1_contextual_transition_review/"
        "h4_d1_contextual_transition_review_report.txt"
    )
    symbol: str = "EURUSD"
    h4_timeframe: str = "H4"
    d1_timeframe: str = "D1"
    baseline_h4_scenario_count: int = 4
    baseline_d1_scenario_count: int = 4
    minimum_context_count: int = 20
    minimum_d1_regime_count: int = 2
    allow_partial_context: bool = True
    partial_sample_label: str = "PARTIAL_SAMPLE"
