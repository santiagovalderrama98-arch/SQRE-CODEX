"""Models for D1 regime context adequacy review."""

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
class D1RegimeContextAdequacySummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    aligned_h4_transition_row_count: int
    distinct_h4_transition_count: int
    distinct_d1_market_state_count: int
    distinct_d1_regime_count: int
    context_profile_count: int
    research_ready_context_count: int
    low_or_insufficient_context_count: int
    d1_context_count: int
    high_fragmentation_transition_count: int
    extreme_fragmentation_transition_count: int
    high_sample_loss_transition_count: int
    extreme_sample_loss_transition_count: int
    aggregation_candidate_count: int
    dominant_d1_context_adequacy_class: str
    d1_regime_context_adequacy_readiness_flag: str
    d1_regime_context_adequacy_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class D1RegimeContextAdequacyResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    market_state_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    regime_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    concentration_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_sample_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    d1_context_inventory: pd.DataFrame = field(default_factory=pd.DataFrame)
    fragmentation_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_loss_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    d1_context_sample_adequacy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    aggregation_candidate_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: D1RegimeContextAdequacySummary | None = None
