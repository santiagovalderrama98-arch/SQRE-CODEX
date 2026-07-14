"""Configuration for M15 introduction review."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class M15IntroductionReviewConfig:
    duration_reference_seconds: int = 28800
    high_low_sample_threshold: int = 50
    high_structure_cv_threshold: float = 0.25
    duration_near_max_threshold: float = 0.85
    high_state_diversity_threshold: int = 7
    low_state_diversity_threshold: int = 3
    forward_range_cv_threshold: float = 0.25
