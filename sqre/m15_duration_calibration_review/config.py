"""Configuration for M15 duration calibration review."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class M15DurationCalibrationReviewConfig:
    baseline_profile: str = "m15_duration_8h_baseline"
    high_low_sample_threshold: int = 50
    high_structure_cv_threshold: float = 0.25
    duration_near_max_threshold: float = 0.85
    fragmentation_increase_threshold: float = 0.25
    compression_decrease_threshold: float = 0.25
    high_state_diversity_threshold: int = 7
    low_state_diversity_threshold: int = 3
