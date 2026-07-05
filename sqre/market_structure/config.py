"""Configuration for SQRE Market Structure v1.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketStructureConfig:
    pip_size: float = 0.0001
    min_leg_pips: float = 3.0
    min_structure_confidence: float = 0.40
    max_events_without_leg: int = 20
    max_structure_duration_seconds: int | None = None
    density_reference_events_per_hour: float = 20.0
    volatility_reference_pips: float = 15.0
    efficiency_reference_pips_per_event: float = 1.0
    neutral_threshold_pips: float = 3.0
