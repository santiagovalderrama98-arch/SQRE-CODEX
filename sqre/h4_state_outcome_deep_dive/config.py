"""Configuration for H4 state outcome deep dive."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class H4StateOutcomeDeepDiveConfig:
    minimum_total_sample_size: int = 20
    minimum_scenario_count: int = 2
    full_scenario_count: int = 4
    high_dispersion_threshold: float = 0.35
    moderate_dispersion_threshold: float = 0.20
    include_sample_constrained_observations: bool = True
