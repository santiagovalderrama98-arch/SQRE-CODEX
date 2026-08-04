"""Models for Research Reference Store Design."""

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
class ResearchReferenceStoreDesignSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    outcome_profile_count: int
    reference_candidate_count: int
    included_reference_count: int
    core_reference_count: int
    supporting_reference_count: int
    watchlist_reference_count: int
    excluded_reference_count: int
    excluded_sample_constrained_count: int
    excluded_high_dispersion_count: int
    excluded_low_interpretability_count: int
    primary_reference_granularity: str
    primary_reference_horizon: str
    research_reference_store_readiness_class: str
    research_reference_store_readiness_flag: str
    research_reference_store_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ResearchReferenceStoreDesignResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    interpretability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    directional_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    excursion_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    context_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    interpretation_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    forward_outcome_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_adequacy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    dispersion_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    aligned_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    candidates: pd.DataFrame = field(default_factory=pd.DataFrame)
    reference_store: pd.DataFrame = field(default_factory=pd.DataFrame)
    exclusion_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ResearchReferenceStoreDesignSummary | None = None
