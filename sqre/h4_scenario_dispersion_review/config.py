"""Configuration for H4 scenario dispersion review."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class H4ScenarioDispersionReviewConfig:
    moderate_deviation_threshold: float = 0.20
    high_deviation_threshold: float = 0.35
    moderate_dispersion_threshold: float = 0.20
    high_dispersion_threshold: float = 0.35
    minimum_total_sample_size: int = 20
    minimum_scenario_count: int = 2
    full_scenario_count: int = 4
