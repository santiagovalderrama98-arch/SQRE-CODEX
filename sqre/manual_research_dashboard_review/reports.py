"""Output writers for manual research dashboard review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.manual_research_dashboard_review.field_usefulness_review import FIELD_USEFULNESS_COLUMNS
from sqre.manual_research_dashboard_review.models import ManualResearchDashboardReviewResult
from sqre.manual_research_dashboard_review.panel_completeness_review import PANEL_COMPLETENESS_COLUMNS
from sqre.manual_research_dashboard_review.panel_readability_review import PANEL_READABILITY_COLUMNS
from sqre.manual_research_dashboard_review.redundancy_review import REDUNDANCY_REVIEW_COLUMNS
from sqre.manual_research_dashboard_review.refined_html_renderer import render_refined_html
from sqre.manual_research_dashboard_review.refinement_recommendations import REFINEMENT_RECOMMENDATION_COLUMNS
from sqre.manual_research_dashboard_review.scope_safety_review import SCOPE_SAFETY_COLUMNS
from sqre.manual_research_dashboard_review.source_inventory import SOURCE_COLUMNS
from sqre.manual_research_dashboard_review.usability_findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    scope_statements,
)


SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Dashboard_Source_Row_Count",
    "Panel_Completeness_Ready_Count",
    "Panel_Completeness_Partial_Count",
    "Panel_Completeness_Missing_Count",
    "High_Readability_Panel_Count",
    "Moderate_Readability_Panel_Count",
    "Low_Readability_Panel_Count",
    "Core_Field_Count",
    "Supporting_Field_Count",
    "Diagnostic_Field_Count",
    "Redundant_Or_Low_Use_Field_Count",
    "Scope_Safety_Class",
    "Scope_Warning_Count",
    "Scope_Violation_Count",
    "Recommendation_Count",
    "High_Priority_Recommendation_Count",
    "Medium_Priority_Recommendation_Count",
    "Low_Priority_Recommendation_Count",
    "Dashboard_Usability_Readiness_Class",
    "Dashboard_Usability_Readiness_Flag",
    "Dashboard_Usability_Diagnostic",
    "Recommended_Follow_Up",
]


def write_outputs(result: ManualResearchDashboardReviewResult, dashboard_title: str) -> ManualResearchDashboardReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    result.html_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "manual_research_dashboard_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(
        result.output_dir / "manual_research_dashboard_panel_completeness_review.csv",
        result.panel_completeness,
        PANEL_COMPLETENESS_COLUMNS,
    )
    _write_frame(
        result.output_dir / "manual_research_dashboard_panel_readability_review.csv",
        result.panel_readability,
        PANEL_READABILITY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "manual_research_dashboard_field_usefulness_review.csv",
        result.field_usefulness,
        FIELD_USEFULNESS_COLUMNS,
    )
    _write_frame(
        result.output_dir / "manual_research_dashboard_redundancy_review.csv",
        result.redundancy_review,
        REDUNDANCY_REVIEW_COLUMNS,
    )
    _write_frame(
        result.output_dir / "manual_research_dashboard_scope_safety_review.csv",
        result.scope_safety,
        SCOPE_SAFETY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "manual_research_dashboard_refinement_recommendations.csv",
        result.refinement_recommendations,
        REFINEMENT_RECOMMENDATION_COLUMNS,
    )
    _write_rows(
        result.output_dir / "manual_research_dashboard_review_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    result.html_path.write_text(render_refined_html(result, dashboard_title), encoding="utf-8")
    return result


def build_report_text(result: ManualResearchDashboardReviewResult) -> str:
    lines = [
        "SQRE Manual Research Dashboard Review",
        "=====================================",
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
        "Panel Completeness Review",
        "-------------------------",
        *_class_count_lines(result.panel_completeness, "Panel_Completeness_Class"),
        "",
        "Panel Readability Review",
        "------------------------",
        *_class_count_lines(result.panel_readability, "Readability_Class"),
        "",
        "Field Usefulness Review",
        "-----------------------",
        *_class_count_lines(result.field_usefulness, "Field_Usefulness_Class"),
        "",
        "Redundancy Review",
        "-----------------",
        *_class_count_lines(result.redundancy_review, "Potential_Redundancy_Class"),
        "",
        "Scope Safety Review",
        "-------------------",
        *_scope_lines(result),
        "",
        "Refinement Recommendations",
        "--------------------------",
        *_recommendation_lines(result),
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
        "",
        "Refined HTML Output",
        "-------------------",
        str(result.html_path),
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


def _input_directory_lines(result: ManualResearchDashboardReviewResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: ManualResearchDashboardReviewResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:30]]


def _class_count_lines(frame: pd.DataFrame, class_column: str) -> list[str]:
    if frame.empty or class_column not in frame.columns:
        return ["No rows were produced."]
    counts = frame[class_column].value_counts().sort_index()
    return [f"- {name}: {count}" for name, count in counts.items()]


def _scope_lines(result: ManualResearchDashboardReviewResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No scope safety summary was produced."]
    return [
        f"Scope safety class: {summary.scope_safety_class}",
        f"Scope warning count: {summary.scope_warning_count}",
        f"Scope violation count: {summary.scope_violation_count}",
    ]


def _recommendation_lines(result: ManualResearchDashboardReviewResult) -> list[str]:
    if result.refinement_recommendations.empty:
        return ["No refinement recommendations were produced."]
    lines = []
    for _, row in result.refinement_recommendations.head(12).iterrows():
        lines.append(
            f"- {row.get('Recommendation_ID')}: {row.get('Recommendation_Priority')} "
            f"{row.get('Recommendation_Category')} - {row.get('Recommendation_Text')}"
        )
    return lines


def _summary_lines(result: ManualResearchDashboardReviewResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Panel completeness ready count: {summary.panel_completeness_ready_count}",
        f"Panel completeness partial count: {summary.panel_completeness_partial_count}",
        f"Panel completeness missing count: {summary.panel_completeness_missing_count}",
        f"High readability panel count: {summary.high_readability_panel_count}",
        f"Moderate readability panel count: {summary.moderate_readability_panel_count}",
        f"Low readability panel count: {summary.low_readability_panel_count}",
        f"Core field count: {summary.core_field_count}",
        f"Supporting field count: {summary.supporting_field_count}",
        f"Diagnostic field count: {summary.diagnostic_field_count}",
        f"Redundant or low-use field count: {summary.redundant_or_low_use_field_count}",
        f"Recommendation count: {summary.recommendation_count}",
        f"Dashboard usability readiness class: {summary.dashboard_usability_readiness_class}",
        f"Dashboard usability readiness flag: {summary.dashboard_usability_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]
