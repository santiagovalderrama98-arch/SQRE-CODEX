"""Models for H4/D1 same-time contextual transition review."""

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
class ContextualTransitionSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    aligned_h4_transition_row_count: int
    distinct_h4_transition_count: int
    distinct_d1_market_state_count: int
    distinct_d1_regime_count: int
    context_profile_count: int
    research_ready_context_count: int
    moderate_context_count: int
    low_sample_context_count: int
    insufficient_context_count: int
    d1_context_concentrated_transition_count: int
    d1_context_mixed_transition_count: int
    d1_context_dispersed_transition_count: int
    dominant_contextual_review_class: str
    h4_d1_contextual_transition_readiness_flag: str
    h4_d1_contextual_transition_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1SameTimeContextualTransitionReviewResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    transition_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    state_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    coverage_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    alignment_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    market_state_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    regime_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    concentration_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_adequacy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: ContextualTransitionSummary | None = None
