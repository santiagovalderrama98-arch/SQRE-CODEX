"""Configuration for SQRE calibration review diagnostics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationReviewConfig:
    """Diagnostic thresholds for calibration review.

    These thresholds are read-only diagnostics and do not alter runtime
    behavior in other SQRE modules.
    """

    duration_near_max_threshold: float = 0.85
    state_dominance_threshold: float = 0.60
    low_state_diversity_threshold: int = 4
    low_sample_rate_threshold: float = 0.50
    high_directional_ratio_threshold: float = 0.75
