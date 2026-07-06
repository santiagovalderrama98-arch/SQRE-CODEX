"""Dataclass models for SQRE Transition Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class MarketStateInput:
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
    lifecycle_stage: str = ""
    duration_seconds: float = 0.0
    price_displacement: float = 0.0
    event_count: int = 0
    leg_count: int = 0


@dataclass(frozen=True)
class TransitionMetrics:
    persistence_change: float
    complexity_change: float
    stability_change: float
    efficiency_change: float
    density_change: float
    volatility_change: float
    symmetry_change: float
    structural_confidence_change: float
    state_confidence_change: float
    price_displacement_change: float
    duration_change: float
    event_count_change: int
    leg_count_change: int
    persistence_abs_change: float
    complexity_abs_change: float
    stability_abs_change: float
    efficiency_abs_change: float
    density_abs_change: float
    volatility_abs_change: float
    symmetry_abs_change: float
    structural_confidence_abs_change: float
    state_confidence_abs_change: float
    transition_magnitude: float
    transition_stability: float
    structural_quality_change: float


@dataclass(frozen=True)
class StateTransition:
    transition_id: str
    from_state_id: str
    to_state_id: str
    from_structure_id: str
    to_structure_id: str
    symbol: str
    timeframe: str
    from_market_state: str
    to_market_state: str
    transition_label: str
    start_time: datetime
    end_time: datetime
    transition_duration_seconds: float
    from_direction: str
    to_direction: str
    state_changed: bool
    direction_changed: bool
    primary_transition_type: str
    transition_tags: str
    metrics: TransitionMetrics


@dataclass(frozen=True)
class TransitionMatrixRow:
    from_state: str
    to_state: str
    count: int
    probability: float
    percentage: float
    average_transition_magnitude: float
    average_transition_stability: float
    average_state_confidence_change: float
    average_structural_quality_change: float


@dataclass(frozen=True)
class TransitionSequence:
    sequence_id: str
    sequence: str
    length: int
    count: int
    frequency: float
    percentage: float
    average_duration: float
    average_transition_magnitude: float


@dataclass(frozen=True)
class TransitionEngineSummary:
    symbol: str
    timeframe: str
    period_start: datetime | None
    period_end: datetime | None
    states_processed: int
    transitions_generated: int
    unique_states: int
    unique_transitions: int
    most_common_transition: str
    most_common_sequence: str
    state_change_rate: float
    direction_change_rate: float
    average_transition_duration: float
    average_transition_magnitude: float
    average_transition_stability: float
    average_state_confidence_change: float
    average_structural_quality_change: float
    state_transitions_path: Path
    transition_matrix_path: Path
    transition_sequences_path: Path
    report_path: Path
