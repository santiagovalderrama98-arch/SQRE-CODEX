"""Dataclass models for SQRE Market States."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StructuralInput:
    structure_id: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    direction: str
    lifecycle_stage: str
    persistence_index: float
    structural_complexity: float
    structural_stability: float
    structural_efficiency: float
    event_density: float
    structural_volatility: float
    structural_symmetry: float
    structural_confidence: float
    duration_seconds: float | None = None
    price_displacement: float | None = None
    event_count: int | None = None
    leg_count: int | None = None


@dataclass(frozen=True)
class MarketState:
    state_id: str
    structure_id: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    direction: str
    market_state: str
    state_confidence: float
    classification_rule: str
    persistence_index: float
    structural_complexity: float
    structural_stability: float
    structural_efficiency: float
    event_density: float
    structural_volatility: float
    structural_symmetry: float
    structural_confidence: float
    lifecycle_stage: str
    duration_seconds: float | None = None
    price_displacement: float | None = None
    event_count: int | None = None
    leg_count: int | None = None


@dataclass(frozen=True)
class StateClassificationResult:
    market_state: str
    classification_rule: str
