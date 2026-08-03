"""Synchronization quality review for H4/D1 prepared data."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.models import H4ContinuityReviewRow, SynchronizationReviewRow


def build_synchronization_review(
    h4_frame: pd.DataFrame,
    d1_frame: pd.DataFrame,
    alignment_frame: pd.DataFrame,
    continuity: H4ContinuityReviewRow,
    config: H4D1SynchronizedDataPreparationConfig,
) -> SynchronizationReviewRow:
    h4_count = len(h4_frame)
    d1_count = len(d1_frame)
    aligned = int((alignment_frame["H4_D1_Candle_Alignment_Class"] != "H4_D1_CANDLE_ALIGNMENT_MISSING_D1").sum()) if not alignment_frame.empty else 0
    unaligned = h4_count - aligned
    coverage_ratio = round(aligned / h4_count, 4) if h4_count else 0.0
    full_d1 = _count_quality(d1_frame, "FULL_H4_DERIVED_D1_CANDLE")
    partial_d1 = _count_quality(d1_frame, "PARTIAL_H4_DERIVED_D1_CANDLE")
    low_d1 = _count_quality(d1_frame, "LOW_COVERAGE_H4_DERIVED_D1_CANDLE")
    quality = _quality_class(h4_count, coverage_ratio, continuity.continuity_ratio, full_d1, partial_d1, config)
    return SynchronizationReviewRow(
        symbol=config.symbol,
        h4_timeframe="H4",
        d1_timeframe="D1",
        h4_row_count=h4_count,
        d1_row_count=d1_count,
        aligned_h4_row_count=aligned,
        unaligned_h4_row_count=unaligned,
        full_d1_candle_count=full_d1,
        partial_d1_candle_count=partial_d1,
        low_coverage_d1_candle_count=low_d1,
        continuity_ratio=continuity.continuity_ratio,
        synchronization_coverage_ratio=coverage_ratio,
        synchronization_quality_class=quality,
        synchronization_diagnostic=_diagnostic(quality),
    )


def _count_quality(frame: pd.DataFrame, quality: str) -> int:
    if frame.empty or "D1_Candle_Quality_Class" not in frame.columns:
        return 0
    return int((frame["D1_Candle_Quality_Class"] == quality).sum())


def _quality_class(
    h4_count: int,
    coverage_ratio: float,
    continuity_ratio: float,
    full_d1: int,
    partial_d1: int,
    config: H4D1SynchronizedDataPreparationConfig,
) -> str:
    if h4_count == 0:
        return "INPUT_MISSING"
    if continuity_ratio >= config.minimum_h4_continuity_ratio and coverage_ratio >= 1.0 and full_d1 > 0:
        return "READY_SYNCHRONIZED_H4_D1_DATA"
    if coverage_ratio >= 0.80 and (full_d1 > 0 or partial_d1 > 0):
        return "PARTIAL_SYNCHRONIZED_H4_D1_DATA"
    if coverage_ratio > 0:
        return "LOW_QUALITY_SYNCHRONIZED_H4_D1_DATA"
    return "NOT_READY_SYNCHRONIZED_DATA"


def _diagnostic(quality: str) -> str:
    mapping = {
        "READY_SYNCHRONIZED_H4_D1_DATA": "Synchronized H4/D1 OHLC data is ready for later timestamped generation.",
        "PARTIAL_SYNCHRONIZED_H4_D1_DATA": "Synchronized H4/D1 OHLC data is partial and should be reviewed.",
        "LOW_QUALITY_SYNCHRONIZED_H4_D1_DATA": "Synchronized H4/D1 OHLC data has low quality.",
        "NOT_READY_SYNCHRONIZED_DATA": "Synchronized H4/D1 OHLC data is not ready.",
        "INPUT_MISSING": "H4 input data is missing.",
    }
    return mapping.get(quality, "Synchronization quality was classified.")
