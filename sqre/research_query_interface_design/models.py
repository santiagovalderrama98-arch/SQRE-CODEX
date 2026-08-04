"""Models for Research Query Interface Design."""

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
class ResearchQueryInterfaceDesignSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    research_reference_count: int
    research_query_request_count: int
    valid_query_request_count: int
    query_result_count: int
    query_with_result_count: int
    query_without_result_count: int
    research_query_coverage_ratio: float
    high_quality_query_result_count: int
    moderate_quality_query_result_count: int
    low_quality_query_result_count: int
    no_usable_query_result_count: int
    core_evidence_query_result_count: int
    supporting_evidence_query_result_count: int
    primary_query_match_level: str
    primary_query_horizon: str
    dominant_research_query_interface_readiness_class: str
    research_query_interface_readiness_flag: str
    research_query_interface_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ResearchQueryInterfaceDesignResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    reference_store: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_candidates: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_horizon_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_store_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_lookup_results: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_scenarios: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_availability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_horizon_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_evidence_quality_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    interpretability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    directional_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    excursion_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    context_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    interpretation_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    transition_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    state_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    alignment_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_requests: pd.DataFrame = field(default_factory=pd.DataFrame)
    query_results: pd.DataFrame = field(default_factory=pd.DataFrame)
    fallback_trace: pd.DataFrame = field(default_factory=pd.DataFrame)
    evidence_quality_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    coverage_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    result_quality_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ResearchQueryInterfaceDesignSummary | None = None
