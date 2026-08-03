"""Data models for H4 timestamped state/transition output generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SourceInventoryRow:
    source_name: str
    source_type: str
    path: str
    exists: bool
    load_status: str
    rows_loaded: int
    timestamp_columns: str
    scenario_columns: str
    state_columns: str
    transition_columns: str
    diagnostic: str


@dataclass(frozen=True)
class ScenarioInventoryRow:
    scenario_id: str
    symbol: str
    timeframe: str
    period_start: str
    period_end: str
    scenario_status: str
    expected_state_count: int
    expected_transition_count: int
    raw_ohlc_file: str
    raw_ohlc_available: bool
    existing_state_output_available: bool
    existing_transition_output_available: bool
    regeneration_attempted: bool
    regeneration_status: str
    timestamped_state_row_count: int
    timestamped_transition_row_count: int
    scenario_output_coverage_class: str
    scenario_diagnostic: str


@dataclass(frozen=True)
class TimestampedMarketStateRow:
    h4_timestamped_state_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    scenario_period_start: str
    scenario_period_end: str
    state_start_time: str
    state_end_time: str
    state_event_time: str
    state_event_date: str
    market_state: str
    state_confidence: str
    structure_id: str
    structure_direction: str
    structural_efficiency: str
    structural_confidence: str
    state_row_source: str
    state_row_diagnostic: str


@dataclass(frozen=True)
class TimestampedStateTransitionRow:
    h4_timestamped_transition_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    scenario_period_start: str
    scenario_period_end: str
    transition_time: str
    transition_date: str
    source_state: str
    target_state: str
    transition_label: str
    source_state_start_time: str
    source_state_end_time: str
    target_state_start_time: str
    target_state_end_time: str
    source_state_confidence: str
    target_state_confidence: str
    transition_row_source: str
    transition_row_diagnostic: str


@dataclass(frozen=True)
class RegenerationResult:
    scenario_id: str
    attempted: bool
    status: str
    diagnostic: str


@dataclass(frozen=True)
class CoverageReviewRow:
    scenario_id: str
    symbol: str
    timeframe: str
    period_start: str
    period_end: str
    expected_state_count: int
    expected_transition_count: int
    timestamped_state_row_count: int
    timestamped_transition_row_count: int
    state_temporal_key_complete_row_count: int
    transition_temporal_key_complete_row_count: int
    state_coverage_ratio: float
    transition_coverage_ratio: float
    coverage_class: str
    coverage_diagnostic: str


@dataclass(frozen=True)
class MissingOutputReviewRow:
    missing_output_id: str
    scenario_id: str
    missing_output_type: str
    current_source_status: str
    required_source_action: str
    missing_output_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TimestampedStateTransitionSummary:
    symbol: str
    timeframe: str
    scenario_count: int
    source_inventory_row_count: int
    timestamped_state_row_count: int
    timestamped_transition_row_count: int
    scenario_with_full_timestamped_output_count: int
    scenario_with_partial_timestamped_output_count: int
    scenario_with_missing_timestamped_output_count: int
    regenerated_scenario_count: int
    regeneration_failed_scenario_count: int
    dominant_output_coverage_class: str
    h4_timestamped_state_transition_readiness_flag: str
    h4_timestamped_state_transition_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TimestampedStateTransitionResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    scenario_inventory: list[ScenarioInventoryRow] = field(default_factory=list)
    market_state_rows: list[TimestampedMarketStateRow] = field(default_factory=list)
    transition_rows: list[TimestampedStateTransitionRow] = field(default_factory=list)
    coverage_review: list[CoverageReviewRow] = field(default_factory=list)
    missing_output_review: list[MissingOutputReviewRow] = field(default_factory=list)
    summary: H4TimestampedStateTransitionSummary | None = None
