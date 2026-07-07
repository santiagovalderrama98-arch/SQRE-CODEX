"""Dataclass models for SQRE Price Outcome Research."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class PriceOutcomeState:
    state_id: str
    structure_id: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    direction: str
    market_state: str
    state_confidence: float
    duration_seconds: float = 0.0
    price_displacement: float = 0.0


@dataclass(frozen=True)
class PriceOutcomeTransition:
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
    from_direction: str
    to_direction: str
    primary_transition_type: str
    transition_tags: str
    transition_magnitude: float
    transition_stability: float


@dataclass(frozen=True)
class OHLCCandle:
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class PriceOutcomeCondition:
    condition_id: str
    condition_type: str
    condition_value: str
    market_state: str = ""
    transition_label: str = ""
    from_market_state: str = ""
    to_market_state: str = ""


@dataclass(frozen=True)
class PriceOutcomeRow:
    outcome_id: str
    condition_id: str
    condition_type: str
    condition_value: str
    occurrence_id: str
    symbol: str
    timeframe: str
    occurrence_start_time: datetime
    occurrence_end_time: datetime
    reference_time: datetime
    reference_candle_time: datetime
    reference_close: float
    forward_window_candles: int
    forward_end_time: datetime
    future_close: float
    max_future_high: float
    min_future_low: float
    direction: str
    forward_close_return: float
    forward_close_return_pips: float
    forward_close_return_percent: float
    max_favorable_displacement_pips: float
    max_adverse_displacement_pips: float
    forward_range_pips: float
    direction_aligned: bool
    positive_close_return: bool
    negative_close_return: bool
    flat_close_return: bool
    outcome_magnitude_pips: float
    complete_forward_window: bool


@dataclass(frozen=True)
class ConditionPriceOutcomeSummaryRow:
    condition_id: str
    condition_type: str
    condition_value: str
    forward_window_candles: int
    sample_size: int
    incomplete_forward_cases: int
    low_sample_size: bool
    average_forward_close_return_pips: float
    median_forward_close_return_pips: float
    average_forward_range_pips: float
    average_max_favorable_displacement_pips: float
    average_max_adverse_displacement_pips: float
    average_outcome_magnitude_pips: float
    direction_alignment_rate: float
    positive_close_return_rate: float
    negative_close_return_rate: float
    flat_close_return_rate: float


@dataclass(frozen=True)
class PriceOutcomeDistributionRow:
    condition_id: str
    condition_type: str
    condition_value: str
    forward_window_candles: int
    return_bucket: str
    count: int
    frequency: float
    percentage: float
    sample_size: int
    low_sample_size: bool


@dataclass(frozen=True)
class PriceOutcomeResearchSummary:
    symbol: str
    timeframe: str
    period_start: datetime | None
    period_end: datetime | None
    conditions_evaluated: int
    condition_types: list[str]
    price_outcomes_generated: int
    forward_windows: list[int]
    pip_size: float
    minimum_sample_size: int
    summary_rows: int
    distribution_rows: int
    low_sample_conditions: int
    average_forward_close_return_pips: float
    median_forward_close_return_pips: float
    average_forward_range_pips: float
    average_favorable_displacement_pips: float
    average_adverse_displacement_pips: float
    average_outcome_magnitude_pips: float
    direction_alignment_rate: float
    most_observed_condition: str
    largest_average_forward_range_condition: str
    highest_direction_alignment_condition: str
    price_outcomes_path: Path
    condition_price_outcome_summary_path: Path
    price_outcome_distributions_path: Path
    report_path: Path
