"""Pipeline for Phase 7.5.14D H4/D1 synchronized data preparation."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.candle_alignment_mapper import build_h4_d1_alignment_map
from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.d1_aggregator import build_d1_from_h4
from sqre.h4_d1_synchronized_data_preparation.findings import build_summary
from sqre.h4_d1_synchronized_data_preparation.h4_continuity_validator import validate_h4_continuity
from sqre.h4_d1_synchronized_data_preparation.h4_source_resolver import build_source_inventory, resolve_h4_source
from sqre.h4_d1_synchronized_data_preparation.loader import normalize_h4_ohlc
from sqre.h4_d1_synchronized_data_preparation.missing_data_review import build_missing_data_review
from sqre.h4_d1_synchronized_data_preparation.models import H4D1SynchronizedDataPreparationResult
from sqre.h4_d1_synchronized_data_preparation.reports import write_outputs
from sqre.h4_d1_synchronized_data_preparation.synchronization_review import build_synchronization_review


def run_h4_d1_synchronized_data_preparation(
    config: H4D1SynchronizedDataPreparationConfig | None = None,
) -> H4D1SynchronizedDataPreparationResult:
    active_config = config or H4D1SynchronizedDataPreparationConfig()
    h4_source = resolve_h4_source(active_config)
    source_inventory = build_source_inventory(active_config, h4_source)
    normalized = normalize_h4_ohlc(h4_source, active_config.symbol, "H4")
    h4_frame = _filter_date_range(normalized.frame, active_config)
    normalized = _with_filtered_frame(normalized, h4_frame)
    continuity = validate_h4_continuity(normalized, active_config)
    d1_frame = build_d1_from_h4(h4_frame, active_config)
    alignment_frame = build_h4_d1_alignment_map(h4_frame, d1_frame)
    synchronization = build_synchronization_review(h4_frame, d1_frame, alignment_frame, continuity, active_config)
    missing = build_missing_data_review(continuity, synchronization)
    summary = build_summary(synchronization)
    result = H4D1SynchronizedDataPreparationResult(
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        h4_frame=h4_frame,
        continuity_review=continuity,
        d1_frame=d1_frame,
        alignment_frame=alignment_frame,
        synchronization_review=synchronization,
        missing_data_review=missing,
        summary=summary,
    )
    return write_outputs(result)


def _filter_date_range(frame: pd.DataFrame, config: H4D1SynchronizedDataPreparationConfig) -> pd.DataFrame:
    if frame.empty:
        return frame
    filtered = frame.copy()
    timestamps = pd.to_datetime(filtered["Date"], errors="coerce")
    if config.start_date:
        filtered = filtered[timestamps >= pd.to_datetime(config.start_date)]
        timestamps = pd.to_datetime(filtered["Date"], errors="coerce")
    if config.end_date:
        end = pd.to_datetime(config.end_date) + pd.Timedelta(days=1)
        filtered = filtered[timestamps < end]
    return filtered.reset_index(drop=True)


def _with_filtered_frame(normalized, frame: pd.DataFrame):
    return type(normalized)(
        frame=frame,
        input_row_count=normalized.input_row_count,
        normalized_row_count=len(frame),
        parsed_timestamp_count=normalized.parsed_timestamp_count,
        duplicate_timestamp_count=normalized.duplicate_timestamp_count,
        conflicting_duplicate_timestamp_count=normalized.conflicting_duplicate_timestamp_count,
        diagnostic=normalized.diagnostic,
        valid=normalized.valid,
    )
