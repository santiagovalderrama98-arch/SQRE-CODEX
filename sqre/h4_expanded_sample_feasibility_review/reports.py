"""Output writers for H4 expanded sample feasibility review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.models import H4ExpandedSampleFeasibilityResult


SOURCE_INVENTORY_COLUMNS = [
    "source_name",
    "source_type",
    "path",
    "exists",
    "load_status",
    "rows_loaded",
    "h4_rows_loaded",
    "diagnostic",
]

DEFINED_SAMPLE_COLUMNS = [
    "scenario_id",
    "symbol",
    "timeframe",
    "defined_start_date",
    "defined_end_date",
    "source_config",
    "sample_definition_status",
    "sample_definition_diagnostic",
]

RAW_FILE_COLUMNS = [
    "file_path",
    "file_name",
    "partial_file_flag",
    "symbol",
    "timeframe",
    "row_count",
    "first_date",
    "last_date",
    "date_coverage_status",
    "raw_file_diagnostic",
]

AVAILABILITY_COLUMNS = [
    "scenario_id",
    "symbol",
    "timeframe",
    "defined_start_date",
    "defined_end_date",
    "availability_status",
    "coverage_ratio",
    "actual_start_date",
    "actual_end_date",
    "raw_file_path",
    "partial_file_flag",
    "availability_diagnostic",
]

VALIDATION_COLUMNS = [
    "scenario_id",
    "symbol",
    "timeframe",
    "validation_status",
    "ohlc_rows",
    "structure_count",
    "state_count",
    "transition_count",
    "research_output_status",
    "validation_coverage_diagnostic",
]

FEASIBILITY_COLUMNS = [
    "scenario_id",
    "symbol",
    "timeframe",
    "defined_start_date",
    "defined_end_date",
    "availability_status",
    "validation_status",
    "coverage_ratio",
    "raw_file_status",
    "research_output_status",
    "feasibility_class",
    "constraint_class",
    "feasibility_diagnostic",
    "recommended_follow_up",
]

CANDIDATE_COLUMNS = FEASIBILITY_COLUMNS + ["candidate_rationale"]
CONSTRAINED_COLUMNS = FEASIBILITY_COLUMNS + ["constraint_rationale"]

SUMMARY_COLUMNS = [
    "timeframe",
    "defined_h4_sample_count",
    "already_validated_count",
    "feasible_full_sample_count",
    "feasible_partial_sample_count",
    "constrained_partial_sample_count",
    "missing_sample_count",
    "unknown_feasibility_count",
    "raw_h4_file_count",
    "partial_h4_file_count",
    "average_coverage_ratio",
    "minimum_coverage_ratio",
    "maximum_coverage_ratio",
    "dominant_constraint_class",
    "h4_expansion_feasibility_profile",
    "h4_expansion_readiness_flag",
    "h4_expansion_feasibility_diagnostic",
    "recommended_follow_up",
]


def write_review_outputs(
    result: H4ExpandedSampleFeasibilityResult,
) -> H4ExpandedSampleFeasibilityResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_sample_source_inventory.csv", result.source_inventory, SOURCE_INVENTORY_COLUMNS)
    _write_rows(result.output_dir / "h4_defined_sample_inventory.csv", result.defined_samples, DEFINED_SAMPLE_COLUMNS)
    _write_rows(result.output_dir / "h4_raw_file_inventory.csv", result.raw_files, RAW_FILE_COLUMNS)
    _write_rows(result.output_dir / "h4_availability_review.csv", result.availability_rows, AVAILABILITY_COLUMNS)
    _write_rows(result.output_dir / "h4_validation_coverage_review.csv", result.validation_rows, VALIDATION_COLUMNS)
    _write_rows(result.output_dir / "h4_expansion_feasibility_matrix.csv", result.feasibility_rows, FEASIBILITY_COLUMNS)
    _write_rows(
        result.output_dir / "h4_feasible_expansion_candidates.csv",
        result.feasible_candidates,
        CANDIDATE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_constrained_or_missing_samples.csv",
        result.constrained_or_missing_samples,
        CONSTRAINED_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_expanded_sample_feasibility_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: H4ExpandedSampleFeasibilityResult) -> str:
    summary = result.summary
    lines = [
        "SQRE H4 Expanded Historical Sample Feasibility Review",
        "====================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Sources",
        "-------------",
        *_source_lines(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        f"Sources reviewed: {len(result.source_inventory)}",
        f"Sources loaded: {sum(1 for row in result.source_inventory if row.load_status == 'present_loaded')}",
        f"H4 source rows loaded: {sum(row.h4_rows_loaded for row in result.source_inventory)}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
        _summary_line(summary, "H4 expansion feasibility profile", "h4_expansion_feasibility_profile"),
        _summary_line(summary, "H4 expansion readiness flag", "h4_expansion_readiness_flag"),
        _summary_line(summary, "Dominant constraint class", "dominant_constraint_class"),
        _summary_line(summary, "Diagnostic", "h4_expansion_feasibility_diagnostic"),
        _summary_line(summary, "Recommended follow-up", "recommended_follow_up"),
        "",
        "Defined H4 Sample Inventory",
        "---------------------------",
        f"Defined H4 samples: {len(result.defined_samples)}",
        _sample_status_lines(result.defined_samples, "sample_definition_status"),
        "",
        "Raw H4 File Inventory",
        "---------------------",
        f"Raw H4 files inspected: {len(result.raw_files)}",
        _summary_line(summary, "Full local raw files", "raw_h4_file_count"),
        _summary_line(summary, "Partial local raw files", "partial_h4_file_count"),
        "",
        "Availability Review",
        "-------------------",
        _sample_status_lines(result.availability_rows, "availability_status"),
        _summary_line(summary, "Average coverage ratio", "average_coverage_ratio"),
        _summary_line(summary, "Minimum coverage ratio", "minimum_coverage_ratio"),
        _summary_line(summary, "Maximum coverage ratio", "maximum_coverage_ratio"),
        "",
        "Validation Coverage Review",
        "--------------------------",
        _sample_status_lines(result.validation_rows, "validation_status"),
        "",
        "Expansion Feasibility Matrix",
        "----------------------------",
        _sample_status_lines(result.feasibility_rows, "feasibility_class"),
        "",
        "Feasible Expansion Candidate Review",
        "-----------------------------------",
        f"Feasible candidate rows: {len(result.feasible_candidates)}",
        *_top_scenarios(result.feasible_candidates),
        "",
        "Constrained or Missing Sample Review",
        "------------------------------------",
        f"Constrained or missing rows: {len(result.constrained_or_missing_samples)}",
        _sample_status_lines(result.feasibility_rows, "constraint_class"),
        "",
        "Research Readiness Assessment",
        "-----------------------------",
        _summary_line(summary, "Readiness flag", "h4_expansion_readiness_flag"),
        _summary_line(summary, "Assessment", "h4_expansion_feasibility_diagnostic"),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        _summary_line(summary, "Follow-up", "recommended_follow_up"),
        "",
        "Do Not Change Yet",
        "-----------------",
        "- Do not change production defaults.",
        "- Do not change research thresholds from this review.",
        "- Do not change the H4 taxonomy from this review.",
        "- Do not add Decision Engine behavior from this review.",
        "",
        "Limitations",
        "-----------",
        "- This report is descriptive and diagnostic only.",
        "- It reviews local file and validation evidence that already exists.",
        "- Missing optional sources may require manual sample review.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    records = []
    for row in rows:
        record = asdict(row)
        records.append({column: record.get(column, "") for column in columns})
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _source_lines(result: H4ExpandedSampleFeasibilityResult) -> list[str]:
    return [f"- {row.source_name}: {row.path} ({row.load_status})" for row in result.source_inventory]


def _summary_line(summary: object | None, label: str, attribute: str) -> str:
    if summary is None:
        return f"{label}: unavailable"
    value = getattr(summary, attribute)
    if isinstance(value, float):
        return f"{label}: {value:.4f}"
    return f"{label}: {value}"


def _sample_status_lines(rows: Iterable[object], attribute: str) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(getattr(row, attribute))
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return "No rows available."
    return "\n".join(f"- {key}: {counts[key]}" for key in sorted(counts))


def _top_scenarios(rows: Iterable[object]) -> list[str]:
    items = list(rows)[:5]
    if not items:
        return ["No feasible candidate rows identified."]
    return [f"- {row.scenario_id}: {row.feasibility_class}, coverage={row.coverage_ratio:.4f}" for row in items]
