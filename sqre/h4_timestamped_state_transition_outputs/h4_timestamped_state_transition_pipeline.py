"""Pipeline for Phase 7.5.14C H4 timestamped state/transition outputs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.findings import build_summary
from sqre.h4_timestamped_state_transition_outputs.missing_output_review import build_missing_output_review
from sqre.h4_timestamped_state_transition_outputs.models import H4TimestampedStateTransitionResult
from sqre.h4_timestamped_state_transition_outputs.output_coverage_review import build_coverage_review
from sqre.h4_timestamped_state_transition_outputs.pipeline_regenerator import evaluate_regeneration_support
from sqre.h4_timestamped_state_transition_outputs.reports import write_review_outputs
from sqre.h4_timestamped_state_transition_outputs.scenario_resolver import load_scenarios, with_runtime_counts
from sqre.h4_timestamped_state_transition_outputs.source_inventory import build_source_inventory
from sqre.h4_timestamped_state_transition_outputs.state_output_normalizer import normalize_state_outputs
from sqre.h4_timestamped_state_transition_outputs.timestamped_output_discovery import discover_timestamped_outputs
from sqre.h4_timestamped_state_transition_outputs.transition_output_normalizer import (
    build_transitions_from_states,
    normalize_transition_outputs,
)


def run_h4_timestamped_state_transition_outputs(
    config: H4TimestampedStateTransitionConfig | None = None,
) -> H4TimestampedStateTransitionResult:
    active_config = config or H4TimestampedStateTransitionConfig()
    source_inventory = build_source_inventory(active_config)
    scenarios = load_scenarios(active_config)
    discovery_roots = _discovery_roots(active_config)
    sources = discover_timestamped_outputs(discovery_roots)
    state_rows = normalize_state_outputs(sources, scenarios, active_config.symbol, active_config.timeframe)
    transition_rows = normalize_transition_outputs(sources, scenarios, active_config.symbol, active_config.timeframe)
    if state_rows and not transition_rows:
        transition_rows = build_transitions_from_states(state_rows)
    regeneration = evaluate_regeneration_support(scenarios, active_config)
    state_counts = Counter(row.scenario_id for row in state_rows)
    transition_counts = Counter(row.scenario_id for row in transition_rows)
    regeneration_status = {row.scenario_id: (row.attempted, row.status) for row in regeneration}
    enriched_scenarios = with_runtime_counts(scenarios, state_counts, transition_counts, regeneration_status)
    coverage = build_coverage_review(enriched_scenarios, state_rows, transition_rows, active_config)
    missing = build_missing_output_review(coverage)
    summary = build_summary(
        source_inventory,
        coverage,
        state_rows,
        transition_rows,
        regeneration,
        active_config.symbol,
        active_config.timeframe,
    )
    result = H4TimestampedStateTransitionResult(
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        scenario_inventory=enriched_scenarios,
        market_state_rows=state_rows,
        transition_rows=transition_rows,
        coverage_review=coverage,
        missing_output_review=missing,
        summary=summary,
    )
    return write_review_outputs(result)


def _discovery_roots(config: H4TimestampedStateTransitionConfig) -> list[Path]:
    roots = [config.h4_d1_validation_dir, config.h4_d1_structural_research_dir]
    defaults = H4TimestampedStateTransitionConfig()
    if (
        config.h4_d1_validation_dir == defaults.h4_d1_validation_dir
        and config.h4_d1_structural_research_dir == defaults.h4_d1_structural_research_dir
    ):
        roots.extend([Path("data/processed"), Path("data/research")])
    return roots
