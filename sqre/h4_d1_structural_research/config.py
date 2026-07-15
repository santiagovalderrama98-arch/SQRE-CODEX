"""Configuration for H4/D1 structural research."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class H4D1StructuralResearchConfig:
    minimum_sample_size: int = 5
    high_low_sample_rate: float = 0.50
    high_scenario_cv_threshold: float = 0.35
    high_regime_sensitivity_threshold: float = 0.35
    forward_range_stability_threshold: float = 0.30
