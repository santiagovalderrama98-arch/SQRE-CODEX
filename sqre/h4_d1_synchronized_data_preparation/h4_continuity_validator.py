"""H4 timestamp continuity validation."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.models import H4ContinuityReviewRow, NormalizedOhlcResult


EXPECTED_H4_DELTA = pd.Timedelta(hours=4)


def validate_h4_continuity(
    normalized: NormalizedOhlcResult,
    config: H4D1SynchronizedDataPreparationConfig,
) -> H4ContinuityReviewRow:
    frame = normalized.frame.copy()
    if frame.empty:
        return _row(config, normalized, "", "", 0, 0, 0, 0, 0.0, "H4_INPUT_MISSING", "H4 input data is missing.")
    if not normalized.valid or normalized.conflicting_duplicate_timestamp_count > 0:
        return _row(
            config,
            normalized,
            str(frame["Date"].min()),
            str(frame["Date"].max()),
            0,
            0,
            0,
            0.0,
            "INVALID_H4_TIMESTAMPS",
            normalized.diagnostic,
        )

    timestamps = pd.to_datetime(frame["Date"], errors="coerce").dropna().sort_values().reset_index(drop=True)
    deltas = timestamps.diff().dropna()
    gaps = [delta for delta in deltas if delta > EXPECTED_H4_DELTA]
    large_gaps = [delta for delta in gaps if delta > pd.Timedelta(days=3)]
    weekend_gaps = _weekend_gap_count(timestamps)
    ordinary_missing = sum(max(int(delta / EXPECTED_H4_DELTA) - 1, 0) for delta in gaps) - weekend_gaps
    ordinary_missing = max(ordinary_missing, 0)
    expected = max((len(timestamps) - 1) + ordinary_missing, 1)
    continuity_ratio = round((len(timestamps) - 1) / expected, 4) if len(timestamps) > 1 else 1.0
    continuity_class = _continuity_class(normalized, continuity_ratio, config.minimum_h4_continuity_ratio)
    return _row(
        config,
        normalized,
        timestamps.min().strftime("%Y-%m-%d %H:%M:%S"),
        timestamps.max().strftime("%Y-%m-%d %H:%M:%S"),
        len(gaps),
        len(large_gaps),
        weekend_gaps,
        ordinary_missing,
        continuity_ratio,
        continuity_class,
        _diagnostic(continuity_class),
    )


def _weekend_gap_count(timestamps: pd.Series) -> int:
    count = 0
    for previous, current in zip(timestamps, timestamps[1:]):
        if current - previous <= EXPECTED_H4_DELTA:
            continue
        if previous.weekday() == 4 and current.weekday() in {0, 6}:
            count += 1
        elif previous.weekday() in {5, 6} or current.weekday() in {5, 6}:
            count += 1
    return count


def _continuity_class(normalized: NormalizedOhlcResult, ratio: float, minimum: float) -> str:
    if not normalized.valid:
        return "INVALID_H4_TIMESTAMPS"
    if ratio >= 1.0:
        return "FULL_H4_CONTINUITY"
    if ratio >= minimum:
        return "ACCEPTABLE_H4_CONTINUITY"
    if ratio >= 0.50:
        return "PARTIAL_H4_CONTINUITY"
    return "LOW_H4_CONTINUITY"


def _diagnostic(continuity_class: str) -> str:
    mapping = {
        "FULL_H4_CONTINUITY": "H4 timestamps are sorted, unique, and continuous.",
        "ACCEPTABLE_H4_CONTINUITY": "H4 timestamps have acceptable continuity for research preparation.",
        "PARTIAL_H4_CONTINUITY": "H4 timestamps have partial continuity and need review.",
        "LOW_H4_CONTINUITY": "H4 timestamps have low continuity.",
        "INVALID_H4_TIMESTAMPS": "H4 timestamps are invalid or conflicting.",
        "H4_INPUT_MISSING": "H4 input data is missing.",
    }
    return mapping.get(continuity_class, "H4 continuity was classified.")


def _row(
    config: H4D1SynchronizedDataPreparationConfig,
    normalized: NormalizedOhlcResult,
    period_start: str,
    period_end: str,
    gap_count: int,
    large_gap_count: int,
    weekend_gap_count: int,
    missing_count: int,
    ratio: float,
    continuity_class: str,
    diagnostic: str,
) -> H4ContinuityReviewRow:
    return H4ContinuityReviewRow(
        symbol=config.symbol,
        timeframe="H4",
        input_row_count=normalized.input_row_count,
        normalized_row_count=normalized.normalized_row_count,
        period_start=period_start,
        period_end=period_end,
        parsed_timestamp_count=normalized.parsed_timestamp_count,
        duplicate_timestamp_count=normalized.duplicate_timestamp_count,
        conflicting_duplicate_timestamp_count=normalized.conflicting_duplicate_timestamp_count,
        gap_count=gap_count,
        large_gap_count=large_gap_count,
        weekend_gap_count=weekend_gap_count,
        estimated_missing_h4_candle_count=missing_count,
        continuity_ratio=ratio,
        h4_continuity_class=continuity_class,
        continuity_diagnostic=diagnostic,
    )
