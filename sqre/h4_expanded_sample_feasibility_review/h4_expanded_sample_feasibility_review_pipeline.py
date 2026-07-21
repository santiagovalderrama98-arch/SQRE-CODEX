"""Pipeline for H4 expanded historical sample feasibility review."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_expanded_sample_feasibility_review.availability_review import build_availability_review
from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.feasibility_classifier import (
    build_constrained_or_missing_samples,
    build_feasibility_matrix,
    build_feasible_candidates,
    build_summary,
)
from sqre.h4_expanded_sample_feasibility_review.loader import load_csv_source, load_yaml_source
from sqre.h4_expanded_sample_feasibility_review.models import H4ExpandedSampleFeasibilityResult
from sqre.h4_expanded_sample_feasibility_review.raw_file_inspector import inspect_h4_raw_files
from sqre.h4_expanded_sample_feasibility_review.reports import write_review_outputs
from sqre.h4_expanded_sample_feasibility_review.sample_inventory import (
    extract_h4_samples_from_config,
    merge_defined_samples,
)
from sqre.h4_expanded_sample_feasibility_review.validation_coverage_review import build_validation_coverage_review


def run_h4_expanded_sample_feasibility_review(
    output_dir: Path | str,
    report_path: Path | str,
    config: H4ExpandedSampleFeasibilityConfig | None = None,
) -> H4ExpandedSampleFeasibilityResult:
    active_config = config or H4ExpandedSampleFeasibilityConfig()

    sample_config, sample_source = load_yaml_source(active_config.sample_config, "expanded_historical_samples")
    expanded_config, expanded_source = load_yaml_source(
        active_config.expanded_validation_config,
        "expanded_historical_validation",
    )
    h4_d1_config, h4_d1_source = load_yaml_source(
        active_config.h4_d1_validation_config,
        "h4_d1_structural_research_validation",
    )
    availability_frame, availability_source = load_csv_source(
        active_config.availability_csv,
        "expanded_historical_data_availability",
        "csv_summary",
    )
    master_frame, master_source = load_csv_source(
        active_config.master_summary_csv,
        "master_historical_summary",
        "csv_summary",
    )
    expanded_frame, expanded_source_csv = load_csv_source(
        active_config.expanded_summary_csv,
        "all_timeframes_expanded_summary",
        "csv_summary",
    )
    h4_d1_frame, h4_d1_summary_source = load_csv_source(
        active_config.h4_d1_validation_summary,
        "h4_d1_validation_summary",
        "csv_summary",
    )
    h4_d1_research_frame, h4_d1_research_source = load_csv_source(
        active_config.h4_d1_research_dir / "h4_d1_timeframe_research_summary.csv",
        "h4_d1_timeframe_research_summary",
        "csv_summary",
    )
    h4_d1_inventory_frame, h4_d1_inventory_source = load_csv_source(
        active_config.h4_d1_research_dir / "h4_d1_scenario_inventory.csv",
        "h4_d1_scenario_inventory",
        "csv_summary",
    )

    source_inventory = [
        sample_source,
        expanded_source,
        h4_d1_source,
        availability_source,
        master_source,
        expanded_source_csv,
        h4_d1_summary_source,
        h4_d1_research_source,
        h4_d1_inventory_source,
    ]
    defined_samples = merge_defined_samples(
        [
            extract_h4_samples_from_config(sample_config, active_config.sample_config),
            extract_h4_samples_from_config(expanded_config, active_config.expanded_validation_config),
            extract_h4_samples_from_config(h4_d1_config, active_config.h4_d1_validation_config),
        ]
    )
    raw_files = inspect_h4_raw_files(active_config.raw_data_dir, active_config.partial_data_dir)
    availability_rows = build_availability_review(defined_samples, availability_frame, raw_files, active_config)
    validation_rows = build_validation_coverage_review(
        availability_rows,
        [master_frame, expanded_frame, h4_d1_frame, h4_d1_research_frame, h4_d1_inventory_frame],
        active_config.h4_d1_research_dir,
    )
    feasibility_rows = build_feasibility_matrix(availability_rows, validation_rows, active_config)
    feasible_candidates = build_feasible_candidates(feasibility_rows)
    constrained_or_missing_samples = build_constrained_or_missing_samples(feasibility_rows)
    summary = build_summary(len(defined_samples), raw_files, feasibility_rows)

    result = H4ExpandedSampleFeasibilityResult(
        output_dir=Path(output_dir),
        report_path=Path(report_path),
        source_inventory=source_inventory,
        defined_samples=defined_samples,
        raw_files=raw_files,
        availability_rows=availability_rows,
        validation_rows=validation_rows,
        feasibility_rows=feasibility_rows,
        feasible_candidates=feasible_candidates,
        constrained_or_missing_samples=constrained_or_missing_samples,
        summary=summary,
    )
    return write_review_outputs(result)
