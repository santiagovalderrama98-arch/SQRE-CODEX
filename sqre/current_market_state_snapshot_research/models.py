"""Models for Current Market State Snapshot Research."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


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
class CurrentMarketStateSnapshotResearchSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    snapshot_mode: str
    snapshot_source: str
    snapshot_timestamp: str
    snapshot_timestamp_status: str
    snapshot_validation_status: str
    research_reference_count: int
    snapshot_query_count: int
    snapshot_result_count: int
    snapshot_query_with_result_count: int
    snapshot_query_without_result_count: int
    snapshot_reference_coverage_ratio: float
    high_evidence_snapshot_result_count: int
    moderate_evidence_snapshot_result_count: int
    low_evidence_snapshot_result_count: int
    no_usable_snapshot_result_count: int
    core_evidence_snapshot_result_count: int
    supporting_evidence_snapshot_result_count: int
    primary_snapshot_query_match_level: str
    primary_snapshot_horizon: str
    dominant_current_market_state_snapshot_readiness_class: str
    current_market_state_snapshot_readiness_flag: str
    current_market_state_snapshot_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class CurrentMarketStateSnapshotResearchResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    reference_store: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_candidates: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_horizon_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_store_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_requests_input: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_results_input: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_fallback_trace_input: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_evidence_quality_input: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_coverage_input: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_result_quality_input: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_interface_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_lookup_results: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_scenarios: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    transition_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    state_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    alignment_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    h4_timestamped_states: pd.DataFrame = field(default_factory=pd.DataFrame)
    h4_timestamped_transitions: pd.DataFrame = field(default_factory=pd.DataFrame)
    d1_timestamped_states: pd.DataFrame = field(default_factory=pd.DataFrame)
    timestamped_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_context: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_query_requests: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_reference_results: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_fallback_trace: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_evidence_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_behavior_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    snapshot_diagnostic_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: CurrentMarketStateSnapshotResearchSummary | None = None
