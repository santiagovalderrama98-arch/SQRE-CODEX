"""Models for H4/D1 same-time alignment table generation."""

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
class D1ContextMatch:
    row: dict[str, object] | None
    alignment_method: str
    alignment_confidence_class: str
    alignment_diagnostic: str


@dataclass(frozen=True)
class AlignmentCoverageReviewRow:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_transition_row_count: int
    aligned_h4_transition_row_count: int
    unaligned_h4_transition_row_count: int
    h4_state_row_count: int
    aligned_h4_state_row_count: int
    unaligned_h4_state_row_count: int
    d1_state_row_count: int
    transition_alignment_ratio: float
    state_alignment_ratio: float
    transition_alignment_coverage_class: str
    state_alignment_coverage_class: str
    overall_alignment_coverage_class: str
    coverage_diagnostic: str


@dataclass(frozen=True)
class UnmatchedAlignmentReviewRow:
    unmatched_id: str
    unmatched_source_type: str
    h4_source_id: str
    h4_timestamp: str
    h4_date: str
    missing_match_type: str
    current_status: str
    required_source_action: str
    unmatched_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1SameTimeAlignmentSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_transition_row_count: int
    aligned_h4_transition_row_count: int
    unaligned_h4_transition_row_count: int
    h4_state_row_count: int
    aligned_h4_state_row_count: int
    unaligned_h4_state_row_count: int
    d1_state_row_count: int
    transition_alignment_ratio: float
    state_alignment_ratio: float
    dominant_alignment_coverage_class: str
    h4_d1_same_time_alignment_readiness_flag: str
    h4_d1_same_time_alignment_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1SameTimeAlignmentResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    h4_transitions: pd.DataFrame = field(default_factory=pd.DataFrame)
    h4_states: pd.DataFrame = field(default_factory=pd.DataFrame)
    d1_states: pd.DataFrame = field(default_factory=pd.DataFrame)
    candle_alignment_map: pd.DataFrame = field(default_factory=pd.DataFrame)
    transition_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    state_alignment: pd.DataFrame = field(default_factory=pd.DataFrame)
    coverage_review: AlignmentCoverageReviewRow | None = None
    unmatched_review: list[UnmatchedAlignmentReviewRow] = field(default_factory=list)
    summary: H4D1SameTimeAlignmentSummary | None = None
