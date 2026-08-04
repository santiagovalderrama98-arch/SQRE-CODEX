"""Models for Research Reference Store Usage Review."""

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
class ResearchReferenceStoreUsageSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    research_reference_count: int
    usage_scenario_count: int
    matched_scenario_count: int
    unmatched_scenario_count: int
    reference_availability_ratio: float
    high_quality_match_count: int
    moderate_quality_match_count: int
    low_quality_match_count: int
    no_usable_match_count: int
    core_evidence_match_count: int
    supporting_evidence_match_count: int
    primary_usage_granularity: str
    primary_usage_horizon: str
    dominant_reference_usage_readiness_class: str
    research_reference_store_usage_readiness_flag: str
    research_reference_store_usage_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ResearchReferenceStoreUsageReviewResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    reference_store: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_candidates: pd.DataFrame = field(default_factory=pd.DataFrame)
    exclusion_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_horizon_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_store_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    interpretability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    directional_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    excursion_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    context_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    interpretation_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    transition_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    state_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    alignment_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    usage_scenarios: pd.DataFrame = field(default_factory=pd.DataFrame)
    lookup_results: pd.DataFrame = field(default_factory=pd.DataFrame)
    availability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    granularity_usage_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_usage_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    evidence_quality_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ResearchReferenceStoreUsageSummary | None = None
