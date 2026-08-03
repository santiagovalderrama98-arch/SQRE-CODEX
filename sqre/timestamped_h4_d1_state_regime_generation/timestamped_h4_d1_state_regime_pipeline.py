"""Pipeline for timestamped H4/D1 state and regime table generation."""

from __future__ import annotations

from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.coverage_review import build_coverage_review
from sqre.timestamped_h4_d1_state_regime_generation.d1_state_regime_table_builder import build_d1_state_regime_table
from sqre.timestamped_h4_d1_state_regime_generation.findings import build_summary
from sqre.timestamped_h4_d1_state_regime_generation.h4_state_table_builder import build_h4_state_table
from sqre.timestamped_h4_d1_state_regime_generation.h4_transition_table_builder import build_h4_transition_table
from sqre.timestamped_h4_d1_state_regime_generation.loader import (
    load_alignment_map,
    load_d1_ohlc,
    load_h4_ohlc,
    load_synchronized_summary,
)
from sqre.timestamped_h4_d1_state_regime_generation.missing_output_review import build_missing_output_review
from sqre.timestamped_h4_d1_state_regime_generation.models import TimestampedH4D1StateRegimeGenerationResult
from sqre.timestamped_h4_d1_state_regime_generation.reports import write_outputs
from sqre.timestamped_h4_d1_state_regime_generation.source_inventory import build_source_inventory


def run_timestamped_h4_d1_state_regime_generation(
    config: TimestampedH4D1StateRegimeGenerationConfig | None = None,
) -> TimestampedH4D1StateRegimeGenerationResult:
    resolved_config = config or TimestampedH4D1StateRegimeGenerationConfig()
    h4_frame = load_h4_ohlc(resolved_config.synchronized_data_dir)
    d1_frame = load_d1_ohlc(resolved_config.synchronized_data_dir)
    h4_states = build_h4_state_table(
        h4_frame,
        symbol=resolved_config.symbol,
        timeframe=resolved_config.h4_timeframe,
        window_size=resolved_config.h4_window_size,
    )
    h4_transitions = build_h4_transition_table(h4_states)
    d1_states = build_d1_state_regime_table(
        d1_frame,
        symbol=resolved_config.symbol,
        timeframe=resolved_config.d1_timeframe,
        window_size=resolved_config.d1_window_size,
    )
    coverage = build_coverage_review(
        h4_input_count=len(h4_frame),
        d1_input_count=len(d1_frame),
        h4_state_count=len(h4_states),
        h4_transition_count=len(h4_transitions),
        d1_state_count=len(d1_states),
        config=resolved_config,
    )
    missing_review = build_missing_output_review(coverage)
    result = TimestampedH4D1StateRegimeGenerationResult(
        output_dir=resolved_config.output_dir,
        report_path=resolved_config.report_path,
        source_inventory=build_source_inventory(resolved_config.synchronized_data_dir),
        h4_input_frame=h4_frame,
        d1_input_frame=d1_frame,
        alignment_frame=load_alignment_map(resolved_config.synchronized_data_dir),
        synchronized_summary_frame=load_synchronized_summary(resolved_config.synchronized_data_dir),
        h4_states=h4_states,
        h4_transitions=h4_transitions,
        d1_states=d1_states,
        coverage_review=coverage,
        missing_output_review=missing_review,
        summary=build_summary(coverage),
    )
    return write_outputs(result)
