"""Pipeline for H4/D1 same-time alignment table generation."""

from __future__ import annotations

from sqre.h4_d1_same_time_alignment_table.alignment_coverage_review import build_alignment_coverage_review
from sqre.h4_d1_same_time_alignment_table.config import H4D1SameTimeAlignmentConfig
from sqre.h4_d1_same_time_alignment_table.d1_context_index import D1ContextIndex
from sqre.h4_d1_same_time_alignment_table.findings import build_summary
from sqre.h4_d1_same_time_alignment_table.h4_state_alignment_builder import build_h4_state_alignment
from sqre.h4_d1_same_time_alignment_table.h4_transition_alignment_builder import build_h4_transition_alignment
from sqre.h4_d1_same_time_alignment_table.loader import (
    load_candle_alignment_map,
    load_d1_states,
    load_h4_states,
    load_h4_transitions,
)
from sqre.h4_d1_same_time_alignment_table.models import H4D1SameTimeAlignmentResult
from sqre.h4_d1_same_time_alignment_table.reports import write_outputs
from sqre.h4_d1_same_time_alignment_table.source_inventory import build_source_inventory
from sqre.h4_d1_same_time_alignment_table.unmatched_alignment_review import build_unmatched_alignment_review


def run_h4_d1_same_time_alignment_table(
    config: H4D1SameTimeAlignmentConfig | None = None,
) -> H4D1SameTimeAlignmentResult:
    resolved_config = config or H4D1SameTimeAlignmentConfig()
    h4_transitions = load_h4_transitions(resolved_config.timestamped_state_regime_dir)
    h4_states = load_h4_states(resolved_config.timestamped_state_regime_dir)
    d1_states = load_d1_states(resolved_config.timestamped_state_regime_dir)
    candle_map = load_candle_alignment_map(resolved_config.synchronized_data_dir)
    d1_index = D1ContextIndex(d1_states, candle_map)
    transition_alignment = build_h4_transition_alignment(
        h4_transitions,
        d1_index,
        symbol=resolved_config.symbol,
        h4_timeframe=resolved_config.h4_timeframe,
        d1_timeframe=resolved_config.d1_timeframe,
    )
    state_alignment = build_h4_state_alignment(
        h4_states,
        d1_index,
        symbol=resolved_config.symbol,
        h4_timeframe=resolved_config.h4_timeframe,
        d1_timeframe=resolved_config.d1_timeframe,
    )
    coverage = build_alignment_coverage_review(
        transition_alignment,
        state_alignment,
        d1_states,
        resolved_config,
    )
    unmatched = build_unmatched_alignment_review(
        transition_alignment,
        state_alignment,
        d1_state_count=len(d1_states),
    )
    result = H4D1SameTimeAlignmentResult(
        output_dir=resolved_config.output_dir,
        report_path=resolved_config.report_path,
        source_inventory=build_source_inventory(
            resolved_config.timestamped_state_regime_dir,
            resolved_config.synchronized_data_dir,
        ),
        h4_transitions=h4_transitions,
        h4_states=h4_states,
        d1_states=d1_states,
        candle_alignment_map=candle_map,
        transition_alignment=transition_alignment,
        state_alignment=state_alignment,
        coverage_review=coverage,
        unmatched_review=unmatched,
        summary=build_summary(coverage),
    )
    return write_outputs(result)
