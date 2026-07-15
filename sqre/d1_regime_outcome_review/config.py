"""Configuration for D1 regime outcome review."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class D1RegimeOutcomeReviewConfig:
    minimum_total_sample_size: int = 20
    minimum_regime_count: int = 2
    full_regime_count: int = 4
    moderate_dispersion_threshold: float = 0.20
    high_dispersion_threshold: float = 0.35
    moderate_sensitivity_threshold: float = 0.20
    high_sensitivity_threshold: float = 0.35
    low_sample_share_threshold: float = 0.50
