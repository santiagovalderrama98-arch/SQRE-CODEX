"""Dataclass models for SQRE Research Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ResearchMarketState:
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
class ResearchTransition:
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
    transition_magnitude: float
    transition_stability: float
    state_confidence_change: float
    structural_quality_change: float


@dataclass(frozen=True)
class ResearchCondition:
    condition_id: str
    condition_type: str
    condition_value: str
    market_state: str = ""
    from_market_state: str = ""
    to_market_state: str = ""
    transition_label: str = ""
    tag: str = ""
    sequence: str = ""
    sequence_length: int = 0


@dataclass(frozen=True)
class ForwardStateDistributionRow:
    condition_id: str
    condition_type: str
    condition_value: str
    forward_window: int
    observed_forward_state: str
    count: int
    frequency: float
    percentage: float
    sample_size: int
    incomplete_forward_cases: int
    average_forward_state_confidence: float
    average_forward_state_duration: float
    low_sample_size: bool


@dataclass(frozen=True)
class ForwardTransitionDistributionRow:
    condition_id: str
    condition_type: str
    condition_value: str
    observed_forward_transition: str
    count: int
    frequency: float
    percentage: float
    sample_size: int
    average_forward_transition_magnitude: float
    average_forward_transition_stability: float
    average_forward_state_confidence_change: float
    low_sample_size: bool


@dataclass(frozen=True)
class PrecedingStateDistributionRow:
    condition_id: str
    condition_type: str
    condition_value: str
    observed_preceding_state: str
    count: int
    frequency: float
    percentage: float
    sample_size: int
    average_preceding_state_confidence: float
    average_preceding_state_duration: float
    low_sample_size: bool


@dataclass(frozen=True)
class SequenceOutcomeRow:
    condition_id: str
    condition_type: str
    sequence: str
    sequence_length: int
    observed_forward_state: str
    count: int
    frequency: float
    percentage: float
    sample_size: int
    incomplete_forward_cases: int
    average_forward_state_confidence: float
    low_sample_size: bool


@dataclass(frozen=True)
class ConditionSummaryRow:
    condition_id: str
    condition_type: str
    condition_value: str
    sample_size: int
    low_sample_size: bool
    most_common_forward_state: str
    most_common_forward_state_frequency: float
    forward_state_diversity: int
    most_common_preceding_state: str
    most_common_preceding_state_frequency: float
    average_forward_state_confidence: float
    average_forward_transition_magnitude: float
    average_forward_transition_stability: float
    incomplete_forward_cases: int


@dataclass(frozen=True)
class ResearchEngineSummary:
    symbol: str
    timeframe: str
    period_start: datetime | None
    period_end: datetime | None
    states_processed: int
    transitions_processed: int
    conditions_evaluated: int
    forward_windows: list[int]
    minimum_sample_size: int
    forward_state_rows: int
    forward_transition_rows: int
    preceding_state_rows: int
    sequence_outcome_rows: int
    condition_summary_rows: int
    low_sample_conditions: int
    most_common_forward_state_result: str
    most_common_preceding_state_result: str
    most_common_sequence_outcome: str
    forward_state_distributions_path: Path
    forward_transition_distributions_path: Path
    preceding_state_distributions_path: Path
    sequence_outcomes_path: Path
    condition_summaries_path: Path
    report_path: Path
