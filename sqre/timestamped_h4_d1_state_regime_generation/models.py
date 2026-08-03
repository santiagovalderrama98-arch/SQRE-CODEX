"""Models for timestamped H4/D1 state and regime generation."""

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
class CoverageReviewRow:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_input_row_count: int
    d1_input_row_count: int
    h4_state_row_count: int
    h4_transition_row_count: int
    d1_state_row_count: int
    h4_state_coverage_class: str
    h4_transition_coverage_class: str
    d1_state_coverage_class: str
    coverage_diagnostic: str


@dataclass(frozen=True)
class MissingOutputReviewRow:
    missing_output_id: str
    missing_output_type: str
    current_status: str
    required_source_action: str
    missing_output_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class TimestampedH4D1StateRegimeSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_input_row_count: int
    d1_input_row_count: int
    h4_state_row_count: int
    h4_transition_row_count: int
    d1_state_row_count: int
    dominant_generation_coverage_class: str
    timestamped_h4_d1_state_regime_readiness_flag: str
    timestamped_h4_d1_state_regime_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class TimestampedH4D1StateRegimeGenerationResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    h4_input_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    d1_input_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    alignment_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    synchronized_summary_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    h4_states: pd.DataFrame = field(default_factory=pd.DataFrame)
    h4_transitions: pd.DataFrame = field(default_factory=pd.DataFrame)
    d1_states: pd.DataFrame = field(default_factory=pd.DataFrame)
    coverage_review: CoverageReviewRow | None = None
    missing_output_review: list[MissingOutputReviewRow] = field(default_factory=list)
    summary: TimestampedH4D1StateRegimeSummary | None = None
