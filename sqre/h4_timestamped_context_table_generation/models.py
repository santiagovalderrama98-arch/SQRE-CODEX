"""Data models for H4 timestamped context table generation."""

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
    ohlc_file: str
    scenario_status: str
    states_generated: int
    transitions_generated: int
    timestamped_state_source_available: bool
    timestamped_transition_source_available: bool
    timestamped_context_row_count: int
    scenario_context_coverage_class: str
    scenario_diagnostic: str


@dataclass(frozen=True)
class TimestampedContextRow:
    h4_timestamped_context_id: str
    aggregate_context_id: str
    symbol: str
    timeframe: str
    scenario_id: str
    scenario_period_start: str
    scenario_period_end: str
    h4_event_time: str
    h4_event_date: str
    h4_source_state: str
    h4_target_state: str
    h4_transition_label: str
    h4_forward_window: str
    h4_temporal_key_class: str
    h4_d1_alignment_date_key: str
    aggregate_context_match_method: str
    aggregate_context_match_confidence: str
    context_row_diagnostic: str


@dataclass(frozen=True)
class CoverageReviewRow:
    scenario_id: str
    symbol: str
    timeframe: str
    period_start: str
    period_end: str
    expected_transition_count: int
    timestamped_context_row_count: int
    aggregate_context_matched_row_count: int
    aggregate_context_unmatched_row_count: int
    temporal_key_complete_row_count: int
    temporal_key_incomplete_row_count: int
    coverage_ratio: float
    coverage_class: str
    coverage_diagnostic: str


@dataclass(frozen=True)
class MissingContextReviewRow:
    missing_context_id: str
    scenario_id: str
    missing_source_type: str
    missing_source_diagnostic: str
    required_source_action: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TimestampedContextGenerationSummary:
    symbol: str
    timeframe: str
    scenario_count: int
    timestamped_source_count: int
    timestamped_context_row_count: int
    aggregate_context_matched_row_count: int
    aggregate_context_unmatched_row_count: int
    temporal_key_complete_row_count: int
    temporal_key_incomplete_row_count: int
    full_coverage_scenario_count: int
    partial_coverage_scenario_count: int
    low_coverage_scenario_count: int
    missing_coverage_scenario_count: int
    dominant_coverage_class: str
    h4_timestamped_context_readiness_flag: str
    h4_timestamped_context_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4TimestampedContextGenerationResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    scenario_inventory: list[ScenarioInventoryRow] = field(default_factory=list)
    context_rows: list[TimestampedContextRow] = field(default_factory=list)
    coverage_review: list[CoverageReviewRow] = field(default_factory=list)
    missing_context_review: list[MissingContextReviewRow] = field(default_factory=list)
    summary: H4TimestampedContextGenerationSummary | None = None
