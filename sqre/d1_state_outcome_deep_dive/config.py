"""Configuration for D1 state outcome deep dive."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class D1StateOutcomeDeepDiveConfig:
    minimum_total_sample_size: int = 20
    minimum_regime_count: int = 2
    full_regime_count: int = 4
    high_dispersion_threshold: float = 0.35
    moderate_dispersion_threshold: float = 0.20
    include_regime_sensitive_observations: bool = True
