"""Data models for H4/D1 synchronized historical data preparation."""

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
class NormalizedOhlcResult:
    frame: pd.DataFrame
    input_row_count: int
    normalized_row_count: int
    parsed_timestamp_count: int
    duplicate_timestamp_count: int
    conflicting_duplicate_timestamp_count: int
    diagnostic: str
    valid: bool


@dataclass(frozen=True)
class H4ContinuityReviewRow:
    symbol: str
    timeframe: str
    input_row_count: int
    normalized_row_count: int
    period_start: str
    period_end: str
    parsed_timestamp_count: int
    duplicate_timestamp_count: int
    conflicting_duplicate_timestamp_count: int
    gap_count: int
    large_gap_count: int
    weekend_gap_count: int
    estimated_missing_h4_candle_count: int
    continuity_ratio: float
    h4_continuity_class: str
    continuity_diagnostic: str


@dataclass(frozen=True)
class SynchronizationReviewRow:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_row_count: int
    d1_row_count: int
    aligned_h4_row_count: int
    unaligned_h4_row_count: int
    full_d1_candle_count: int
    partial_d1_candle_count: int
    low_coverage_d1_candle_count: int
    continuity_ratio: float
    synchronization_coverage_ratio: float
    synchronization_quality_class: str
    synchronization_diagnostic: str


@dataclass(frozen=True)
class MissingDataReviewRow:
    missing_data_id: str
    missing_data_type: str
    current_status: str
    required_source_action: str
    missing_data_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1SynchronizedDataSummary:
    symbol: str
    h4_timeframe: str
    d1_timeframe: str
    h4_row_count: int
    d1_row_count: int
    aligned_h4_row_count: int
    unaligned_h4_row_count: int
    full_d1_candle_count: int
    partial_d1_candle_count: int
    low_coverage_d1_candle_count: int
    continuity_ratio: float
    synchronization_coverage_ratio: float
    dominant_synchronization_quality_class: str
    h4_d1_synchronized_data_readiness_flag: str
    h4_d1_synchronized_data_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1SynchronizedDataPreparationResult:
    output_dir: Path
    report_path: Path
    source_inventory: list[SourceInventoryRow] = field(default_factory=list)
    h4_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    continuity_review: H4ContinuityReviewRow | None = None
    d1_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    alignment_frame: pd.DataFrame = field(default_factory=pd.DataFrame)
    synchronization_review: SynchronizationReviewRow | None = None
    missing_data_review: list[MissingDataReviewRow] = field(default_factory=list)
    summary: H4D1SynchronizedDataSummary | None = None
