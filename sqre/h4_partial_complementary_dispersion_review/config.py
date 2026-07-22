"""Configuration for H4 partial sample complementary dispersion review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class H4PartialComplementaryDispersionReviewConfig:
    partial_validation_dir: Path = Path("data/research/h4_targeted_partial_expansion_validation")
    h4_state_dispersion_dir: Path = Path("data/research/h4_scenario_dispersion_review")
    h4_state_sensitive_dir: Path = Path("data/research/h4_scenario_sensitive_state_review")
    h4_transition_dispersion_dir: Path = Path("data/research/h4_transition_scenario_dispersion_review")
    h4_transition_sensitive_dir: Path = Path("data/research/h4_transition_scenario_sensitive_review")
    h4_transition_deep_dive_dir: Path = Path("data/research/h4_transition_outcome_deep_dive")
    output_dir: Path = Path("data/research/h4_partial_complementary_dispersion_review")
    report_path: Path = Path(
        "data/research/h4_partial_complementary_dispersion_review/"
        "h4_partial_complementary_dispersion_review_report.txt"
    )
    candidate_id: str = "eurusd_h4_period_5_partial"
    partial_sample_label: str = "PARTIAL_SAMPLE"
    baseline_scenario_count: int = 4
    consistency_lower_bound: float = 0.70
    consistency_upper_bound: float = 1.30
    minimum_condition_profile_count: int = 20
