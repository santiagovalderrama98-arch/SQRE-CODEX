"""Configuration for H4 transition/state combined context review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4TransitionStateCombinedContextReviewConfig:
    h4_state_deep_dive_dir: Path = Path("data/research/h4_state_outcome_deep_dive")
    h4_state_dispersion_dir: Path = Path("data/research/h4_scenario_dispersion_review")
    h4_state_sensitive_dir: Path = Path("data/research/h4_scenario_sensitive_state_review")
    h4_transition_deep_dive_dir: Path = Path("data/research/h4_transition_outcome_deep_dive")
    h4_transition_dispersion_dir: Path = Path("data/research/h4_transition_scenario_dispersion_review")
    h4_transition_sensitive_dir: Path = Path("data/research/h4_transition_scenario_sensitive_review")
    partial_complement_dir: Path = Path("data/research/h4_partial_complementary_dispersion_review")
    partial_validation_dir: Path = Path("data/research/h4_targeted_partial_expansion_validation")
    output_dir: Path = Path("data/research/h4_transition_state_combined_context_review")
    report_path: Path = Path(
        "data/research/h4_transition_state_combined_context_review/"
        "h4_transition_state_combined_context_review_report.txt"
    )
    timeframe: str = "H4"
    symbol: str = "EURUSD"
    partial_sample_label: str = "PARTIAL_SAMPLE"
    baseline_scenario_count: int = 4
    minimum_transition_sample_size: int = 20
    minimum_state_sample_size: int = 20
    minimum_condition_profile_count: int = 20
    scenario_sensitive_threshold: str = "HIGH"
    allow_partial_context: bool = True
