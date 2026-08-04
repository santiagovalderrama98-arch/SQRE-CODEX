"""Models for H4/D1 aligned forward outcome research."""

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
class PriceAnchor:
    index: int
    timestamp: pd.Timestamp
    close: float


@dataclass(frozen=True)
class H4D1AlignedForwardOutcomeSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    aligned_h4_transition_row_count: int
    forward_outcome_row_count: int
    complete_forward_outcome_row_count: int
    partial_forward_outcome_row_count: int
    missing_forward_outcome_row_count: int
    outcome_profile_count: int
    research_ready_outcome_profile_count: int
    moderate_outcome_profile_count: int
    low_or_insufficient_outcome_profile_count: int
    h4_transition_only_profile_count: int
    h4_transition_d1_market_state_profile_count: int
    h4_transition_d1_regime_profile_count: int
    h4_transition_d1_state_regime_profile_count: int
    dominant_outcome_readiness_class: str
    h4_d1_aligned_forward_outcome_readiness_flag: str
    h4_d1_aligned_forward_outcome_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1AlignedForwardOutcomeResearchResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    transition_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    h4_ohlc: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    forward_outcomes: pd.DataFrame = field(default_factory=pd.DataFrame)
    outcome_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    dispersion_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_adequacy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: H4D1AlignedForwardOutcomeSummary | None = None
