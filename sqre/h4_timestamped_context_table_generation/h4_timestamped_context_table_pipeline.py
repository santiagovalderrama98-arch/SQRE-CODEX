"""Pipeline for Phase 7.5.14B H4 timestamped context table generation."""

from __future__ import annotations

from sqre.h4_timestamped_context_table_generation.aggregate_context_mapper import map_aggregate_contexts
from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.coverage_review import build_coverage_review
from sqre.h4_timestamped_context_table_generation.findings import build_summary
from sqre.h4_timestamped_context_table_generation.missing_key_review import build_missing_context_review
from sqre.h4_timestamped_context_table_generation.models import H4TimestampedContextGenerationResult
from sqre.h4_timestamped_context_table_generation.reports import write_review_outputs
from sqre.h4_timestamped_context_table_generation.scenario_inventory_loader import (
    enrich_scenario_inventory,
    load_base_scenario_inventory,
)
from sqre.h4_timestamped_context_table_generation.source_inventory import build_source_inventory
from sqre.h4_timestamped_context_table_generation.timestamped_source_discovery import discover_timestamped_sources
from sqre.h4_timestamped_context_table_generation.transition_context_extractor import extract_timestamped_context_rows


def run_h4_timestamped_context_table_generation(
    config: H4TimestampedContextTableGenerationConfig | None = None,
) -> H4TimestampedContextGenerationResult:
    active_config = config or H4TimestampedContextTableGenerationConfig()
    source_inventory = build_source_inventory(active_config)
    scenarios = load_base_scenario_inventory(active_config)
    timestamped_sources = discover_timestamped_sources(
        [active_config.h4_d1_validation_dir, active_config.h4_d1_structural_research_dir]
    )
    context_rows, state_scenarios, transition_scenarios = extract_timestamped_context_rows(
        timestamped_sources,
        scenarios,
        active_config,
    )
    mapped_rows = map_aggregate_contexts(context_rows, active_config.h4_combined_context_dir)
    enriched_scenarios = enrich_scenario_inventory(scenarios, mapped_rows, state_scenarios, transition_scenarios)
    coverage = build_coverage_review(enriched_scenarios, mapped_rows, active_config)
    missing = build_missing_context_review(enriched_scenarios)
    summary = build_summary(source_inventory, coverage, mapped_rows, active_config.symbol, active_config.timeframe)
    result = H4TimestampedContextGenerationResult(
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        scenario_inventory=enriched_scenarios,
        context_rows=mapped_rows,
        coverage_review=coverage,
        missing_context_review=missing,
        summary=summary,
    )
    return write_review_outputs(result)
