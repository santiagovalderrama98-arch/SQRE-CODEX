"""Configuration for SQRE Market States v1.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketStatesConfig:
    low_quality_confidence_threshold: float = 0.55
    directional_expansion_persistence_threshold: float = 0.50
    directional_expansion_efficiency_threshold: float = 0.60
    directional_expansion_confidence_threshold: float = 0.65
    directional_drift_persistence_threshold: float = 0.35
    directional_drift_efficiency_threshold: float = 0.60
    directional_drift_confidence_threshold: float = 0.60
    neutral_compression_efficiency_threshold: float = 0.30
    neutral_compression_persistence_threshold: float = 0.50
    complex_consolidation_complexity_threshold: float = 0.70
    complex_consolidation_efficiency_threshold: float = 0.35
    complex_consolidation_density_threshold: float = 0.45
    volatile_rotation_volatility_threshold: float = 0.70
    volatile_rotation_persistence_threshold: float = 0.50
    volatile_rotation_efficiency_threshold: float = 0.50
