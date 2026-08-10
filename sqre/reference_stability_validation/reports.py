"""Output writers for reference stability validation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.reference_stability_validation.dashboard_reference_stability_review import DASHBOARD_COLUMNS
from sqre.reference_stability_validation.directional_consistency_review import DIRECTIONAL_COLUMNS
from sqre.reference_stability_validation.dispersion_stability_review import DISPERSION_COLUMNS
from sqre.reference_stability_validation.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    scope_statements,
)
from sqre.reference_stability_validation.granularity_stability_review import GRANULARITY_COLUMNS
from sqre.reference_stability_validation.horizon_stability_review import HORIZON_COLUMNS
from sqre.reference_stability_validation.match_level_stability_review import MATCH_LEVEL_COLUMNS
from sqre.reference_stability_validation.models import ReferenceStabilityValidationResult
from sqre.reference_stability_validation.reference_population_review import POPULATION_COLUMNS
from sqre.reference_stability_validation.sample_adequacy_review import SAMPLE_COLUMNS
from sqre.reference_stability_validation.source_inventory import SOURCE_COLUMNS
from sqre.reference_stability_validation.stability_scorecard_builder import SCORECARD_COLUMNS


SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Query_Result_Count",
    "Dashboard_Reference_Card_Count",
    "Stable_Horizon_Count",
    "Partial_Horizon_Count",
    "Unstable_Horizon_Count",
    "Stable_Granularity_Count",
    "Partial_Granularity_Count",
    "Fragmented_Granularity_Count",
    "Stable_Sample_Group_Count",
    "Usable_Sample_Group_Count",
    "Low_Sample_Group_Count",
    "Stable_Dispersion_Group_Count",
    "Usable_Dispersion_Group_Count",
    "High_Dispersion_Group_Count",
    "Stable_Match_Level_Count",
    "Fallback_Dependent_Match_Level_Count",
    "Scope_Safety_Status",
    "Dominant_Reference_Stability_Readiness_Class",
    "Reference_Stability_Readiness_Flag",
    "Reference_Stability_Diagnostic",
    "Recommended_Follow_Up",
]


def write_outputs(result: ReferenceStabilityValidationResult) -> ReferenceStabilityValidationResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "reference_stability_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "reference_population_review.csv", result.reference_population_review, POPULATION_COLUMNS)
    _write_frame(result.output_dir / "reference_horizon_stability_review.csv", result.horizon_stability_review, HORIZON_COLUMNS)
    _write_frame(result.output_dir / "reference_granularity_stability_review.csv", result.granularity_stability_review, GRANULARITY_COLUMNS)
    _write_frame(result.output_dir / "reference_sample_adequacy_review.csv", result.sample_adequacy_review, SAMPLE_COLUMNS)
    _write_frame(result.output_dir / "reference_dispersion_stability_review.csv", result.dispersion_stability_review, DISPERSION_COLUMNS)
    _write_frame(result.output_dir / "reference_directional_consistency_review.csv", result.directional_consistency_review, DIRECTIONAL_COLUMNS)
    _write_frame(result.output_dir / "reference_match_level_stability_review.csv", result.match_level_stability_review, MATCH_LEVEL_COLUMNS)
    _write_frame(result.output_dir / "dashboard_reference_stability_review.csv", result.dashboard_reference_stability_review, DASHBOARD_COLUMNS)
    _write_frame(result.output_dir / "reference_stability_scorecard.csv", result.reference_stability_scorecard, SCORECARD_COLUMNS)
    _write_rows(
        result.output_dir / "reference_stability_validation_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: ReferenceStabilityValidationResult) -> str:
    lines = [
        "SQRE Reference Stability Validation",
        "===================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        *_input_directory_lines(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        *_source_lines(result),
        "",
        "Reference Population Review",
        "---------------------------",
        *_first_row_lines(result.reference_population_review, ["Reference_Count", "Core_Reference_Count", "Supporting_Reference_Count", "Reference_Population_Class"]),
        "",
        "Horizon Stability Review",
        "------------------------",
        *_class_count_lines(result.horizon_stability_review, "Horizon_Stability_Class"),
        "",
        "Granularity Stability Review",
        "----------------------------",
        *_class_count_lines(result.granularity_stability_review, "Granularity_Stability_Class"),
        "",
        "Sample Adequacy Review",
        "----------------------",
        *_class_count_lines(result.sample_adequacy_review, "Sample_Adequacy_Class"),
        "",
        "Dispersion Stability Review",
        "---------------------------",
        *_class_count_lines(result.dispersion_stability_review, "Dispersion_Stability_Class"),
        "",
        "Directional Consistency Review",
        "------------------------------",
        *_class_count_lines(result.directional_consistency_review, "Directional_Consistency_Class"),
        "",
        "Match Level Stability Review",
        "----------------------------",
        *_class_count_lines(result.match_level_stability_review, "Match_Level_Stability_Class"),
        "",
        "Dashboard Reference Stability Review",
        "------------------------------------",
        *_first_row_lines(result.dashboard_reference_stability_review, ["Reference_Card_Count", "Dashboard_Reference_Stability_Class"]),
        "",
        "Reference Stability Scorecard",
        "-----------------------------",
        *_scorecard_lines(result.reference_stability_scorecard),
        "",
        "Readiness Assessment",
        "--------------------",
        *_summary_lines(result),
        "",
        "Potential Follow-Up Areas",
        "-------------------------",
        *[f"- {line}" for line in potential_follow_up_areas()],
        "",
        "Do Not Change Yet",
        "-----------------",
        *[f"- {line}" for line in do_not_change_yet_lines()],
        "",
        "Limitations",
        "-----------",
        *[f"- {line}" for line in limitation_lines()],
        "",
        "Scope Statements",
        "----------------",
        *[f"- {line}" for line in scope_statements()],
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows if row is not None]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _write_frame(path: Path, frame: pd.DataFrame, columns: list[str]) -> None:
    pd.DataFrame(frame).reindex(columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(_snake(column), "") for column in columns}


def _snake(name: str) -> str:
    out = []
    for index, char in enumerate(name):
        if char.isupper() and index > 0 and name[index - 1] != "_":
            out.append("_")
        out.append(char.lower())
    return "".join(out)


def _input_directory_lines(result: ReferenceStabilityValidationResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: ReferenceStabilityValidationResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:30]]


def _class_count_lines(frame: pd.DataFrame, class_column: str) -> list[str]:
    if frame.empty or class_column not in frame.columns:
        return ["No rows were produced."]
    counts = frame[class_column].value_counts().sort_index()
    return [f"- {name}: {count}" for name, count in counts.items()]


def _first_row_lines(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    if frame.empty:
        return ["No rows were produced."]
    row = frame.iloc[0]
    return [f"{column}: {row.get(column, '')}" for column in columns]


def _scorecard_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No scorecard rows were produced."]
    return [
        f"- {row.get('Stability_Dimension')}: {row.get('Dominant_Stability_Class')}"
        for _, row in frame.iterrows()
    ]


def _summary_lines(result: ReferenceStabilityValidationResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Reference count: {summary.reference_count}",
        f"Core reference count: {summary.core_reference_count}",
        f"Supporting reference count: {summary.supporting_reference_count}",
        f"Query result count: {summary.query_result_count}",
        f"Dashboard reference card count: {summary.dashboard_reference_card_count}",
        f"Stable horizon count: {summary.stable_horizon_count}",
        f"Partial horizon count: {summary.partial_horizon_count}",
        f"Unstable horizon count: {summary.unstable_horizon_count}",
        f"Stable sample group count: {summary.stable_sample_group_count}",
        f"Usable sample group count: {summary.usable_sample_group_count}",
        f"Low sample group count: {summary.low_sample_group_count}",
        f"Stable dispersion group count: {summary.stable_dispersion_group_count}",
        f"Usable dispersion group count: {summary.usable_dispersion_group_count}",
        f"High dispersion group count: {summary.high_dispersion_group_count}",
        f"Stable match level count: {summary.stable_match_level_count}",
        f"Fallback-dependent match level count: {summary.fallback_dependent_match_level_count}",
        f"Readiness class: {summary.dominant_reference_stability_readiness_class}",
        f"Readiness flag: {summary.reference_stability_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]
