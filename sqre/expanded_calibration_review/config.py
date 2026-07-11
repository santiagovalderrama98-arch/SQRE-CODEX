"""Configuration for expanded historical calibration review diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExpandedCalibrationReviewConfig:
    """Diagnostic thresholds for expanded historical review.

    These thresholds are read-only diagnostics and do not alter SQRE runtime
    behavior or production defaults.
    """

    min_scenarios_per_timeframe: int = 2
    high_low_sample_threshold: int = 50
    high_state_diversity_threshold: int = 7
    low_state_diversity_threshold: int = 3
    high_structure_variation_threshold: float = 0.25
    high_forward_range_variation_threshold: float = 0.35
    high_unclassified_rate_threshold: float = 0.10
    high_low_quality_rate_threshold: float = 0.10
