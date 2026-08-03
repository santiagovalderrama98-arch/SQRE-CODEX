"""Data models for H4/D1 temporal alignment feasibility review."""

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
    diagnostic: str


@dataclass(frozen=True)
class TemporalKeyInventoryRow:
    source_name: str
    source_type: str
    file_name: str
    rows_loaded: int
    timestamp_columns: str
    start_time_columns: str
    end_time_columns: str
    scenario_id_columns: str
    timeframe_columns: str
    condition_only_columns: str
    regime_columns: str
    temporal_key_status: str
    temporal_key_diagnostic: str


@dataclass(frozen=True)
class AlignmentCandidateReviewRow:
    candidate_id: str
    h4_source_name: str
    d1_source_name: str
    h4_key_status: str
    d1_key_status: str
    potential_alignment_method: str
    alignment_feasibility_class: str
    alignment_confidence_class: str
    candidate_diagnostic: str


@dataclass(frozen=True)
class MissingTemporalKeyReviewRow:
    missing_key_id: str
    source_name: str
    source_type: str
    missing_key_type: str
    current_key_status: str
    required_key_for_same_time_alignment: str
    required_source_action: str
    missing_key_diagnostic: str


@dataclass(frozen=True)
class TemporalAlignmentFeasibilitySummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    source_count: int
    loaded_source_count: int
    h4_source_count: int
    d1_source_count: int
    sources_with_exact_timestamp_count: int
    sources_with_start_end_time_count: int
    sources_with_scenario_period_key_count: int
    sources_with_condition_only_key_count: int
    h4_temporal_key_status: str
    d1_temporal_key_status: str
    candidate_count: int
    ready_exact_timestamp_candidate_count: int
    ready_interval_overlap_candidate_count: int
    ready_scenario_period_candidate_count: int
    condition_only_not_temporal_candidate_count: int
    input_limited_candidate_count: int
    dominant_alignment_feasibility_class: str
    temporal_alignment_readiness_flag: str
    temporal_alignment_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class TemporalAlignmentFeasibilityResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    temporal_key_inventory: list[TemporalKeyInventoryRow] = field(default_factory=list)
    alignment_candidates: list[AlignmentCandidateReviewRow] = field(default_factory=list)
    missing_keys: list[MissingTemporalKeyReviewRow] = field(default_factory=list)
    summary: TemporalAlignmentFeasibilitySummary | None = None
