"""Dataclass models for SQRE Market Structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MarketEvent:
    event_id: str
    date: datetime
    event_type: str
    symbol: str
    timeframe: str
    price: float
    value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StructuralPoint:
    point_id: str
    event_id: str
    time: datetime
    point_type: str
    price: float
    source_event_type: str
    priority: int


@dataclass(frozen=True)
class Leg:
    leg_id: str
    structure_id: str
    start_point_id: str
    end_point_id: str
    start_time: datetime
    end_time: datetime
    start_price: float
    end_price: float
    direction: str
    duration_seconds: float
    distance_pips: float
    event_count: int
    expansion_count: int
    contraction_count: int
    large_candle_count: int
    small_candle_count: int
    internal_pivot_count: int
    confidence: float


@dataclass(frozen=True)
class StructuralMetrics:
    event_count: int
    pivot_count: int
    swing_count: int
    large_candle_count: int
    small_candle_count: int
    range_expansion_count: int
    range_contraction_count: int
    leg_count: int
    up_leg_count: int
    down_leg_count: int
    direction_changes: int
    gross_distance_pips: float
    net_displacement_pips: float
    average_leg_distance_pips: float
    max_leg_distance_pips: float
    min_leg_distance_pips: float
    persistence_index: float
    structural_complexity: float
    structural_stability: float
    structural_efficiency: float
    event_density: float
    structural_volatility: float
    structural_symmetry: float
    structural_confidence: float


@dataclass(frozen=True)
class StructuralFingerprint:
    structure_id: str
    persistence: float
    complexity: float
    stability: float
    efficiency: float
    density: float
    volatility: float
    symmetry: float
    confidence: float


@dataclass(frozen=True)
class MarketStructure:
    structure_id: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    start_price: float
    end_price: float
    direction: str
    lifecycle_stage: str
    events: list[MarketEvent]
    points: list[StructuralPoint]
    legs: list[Leg]
    metrics: StructuralMetrics | None = None
    fingerprint: StructuralFingerprint | None = None


@dataclass(frozen=True)
class StructureEventLink:
    structure_id: str
    event_id: str
    event_time: datetime
    event_type: str
    event_price: float
    event_index: int
    role_in_structure: str


@dataclass(frozen=True)
class StructuralUnit:
    unit_id: str
    structure_id: str
    unit_type: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    start_price: float
    end_price: float
    price_displacement: float
    direction: str
    event_count: int
    confidence: float
