"""Models for H4/D1 forward outcome interpretation review."""

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
class H4D1ForwardOutcomeInterpretationSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    outcome_profile_count: int
    interpretable_profile_count: int
    moderately_interpretable_profile_count: int
    low_interpretability_profile_count: int
    sample_constrained_profile_count: int
    high_dispersion_profile_count: int
    upward_dominance_profile_count: int
    downward_dominance_profile_count: int
    mixed_behavior_profile_count: int
    stable_horizon_context_count: int
    unstable_horizon_context_count: int
    best_supported_context_granularity: str
    dominant_interpretation_readiness_class: str
    h4_d1_forward_outcome_interpretation_readiness_flag: str
    h4_d1_forward_outcome_interpretation_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1ForwardOutcomeInterpretationReviewResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    forward_outcomes: pd.DataFrame = field(default_factory=pd.DataFrame)
    outcome_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    dispersion_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_adequacy_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    aligned_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_sample_adequacy: pd.DataFrame = field(default_factory=pd.DataFrame)
    contextual_summary: pd.DataFrame = field(default_factory=pd.DataFrame)
    interpretability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    directional_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    excursion_behavior_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    horizon_stability_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    context_granularity_review: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: H4D1ForwardOutcomeInterpretationSummary | None = None
