"""Configuration for H1/M5 duration calibration review."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeframeDurationCalibrationReviewConfig:
    baseline_profile_h1: str = "h1_duration_24h_baseline"
    baseline_profile_m5: str = "m5_duration_4h_baseline"
    high_low_sample_threshold: int = 50
    high_structure_cv_threshold: float = 0.25
    duration_near_max_threshold: float = 0.85
    fragmentation_increase_threshold: float = 0.25
    compression_decrease_threshold: float = 0.25
