"""Output writers for reference stability documentation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.reference_stability_documentation.dashboard_reading_guide_builder import DASHBOARD_GUIDE_COLUMNS
from sqre.reference_stability_documentation.evidence_usage_policy_builder import USAGE_POLICY_COLUMNS
from sqre.reference_stability_documentation.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    scope_statements,
)
from sqre.reference_stability_documentation.follow_up_documentation_builder import FOLLOW_UP_COLUMNS
from sqre.reference_stability_documentation.limitation_documentation_builder import LIMITATION_COLUMNS
from sqre.reference_stability_documentation.markdown_renderer import render_markdown
from sqre.reference_stability_documentation.models import ReferenceStabilityDocumentationResult
from sqre.reference_stability_documentation.scope_safety_review import SCOPE_SAFETY_COLUMNS
from sqre.reference_stability_documentation.source_inventory import SOURCE_COLUMNS
from sqre.reference_stability_documentation.stability_interpretation_builder import INTERPRETATION_COLUMNS


SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Stability_Dimension_Count",
    "Documented_Stable_Evidence_Count",
    "Documented_Partial_Evidence_Count",
    "Documented_Constrained_Evidence_Count",
    "Documented_Unstable_Evidence_Count",
    "Safe_For_Manual_Research_Review_Count",
    "Use_With_Stability_Warnings_Count",
    "Documentation_Only_Count",
    "Dashboard_Guide_Element_Count",
    "Limitation_Count",
    "Follow_Up_Count",
    "High_Priority_Follow_Up_Count",
    "Medium_Priority_Follow_Up_Count",
    "Low_Priority_Follow_Up_Count",
    "Documentation_Scope_Safety_Class",
    "Scope_Warning_Count",
    "Scope_Violation_Count",
    "Reference_Stability_Documentation_Readiness_Class",
    "Reference_Stability_Documentation_Readiness_Flag",
    "Reference_Stability_Documentation_Diagnostic",
    "Recommended_Follow_Up",
]


def write_outputs(result: ReferenceStabilityDocumentationResult) -> ReferenceStabilityDocumentationResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    result.markdown_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "reference_stability_documentation_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "reference_stability_interpretation_guide.csv", result.interpretation_guide, INTERPRETATION_COLUMNS)
    _write_frame(result.output_dir / "reference_evidence_usage_policy.csv", result.evidence_usage_policy, USAGE_POLICY_COLUMNS)
    _write_frame(result.output_dir / "reference_dashboard_reading_guide.csv", result.dashboard_reading_guide, DASHBOARD_GUIDE_COLUMNS)
    _write_frame(result.output_dir / "reference_stability_limitations_documentation.csv", result.limitations_documentation, LIMITATION_COLUMNS)
    _write_frame(result.output_dir / "reference_stability_follow_up_plan.csv", result.follow_up_plan, FOLLOW_UP_COLUMNS)
    _write_frame(result.output_dir / "reference_stability_documentation_scope_safety_review.csv", result.scope_safety_review, SCOPE_SAFETY_COLUMNS)
    _write_rows(
        result.output_dir / "reference_stability_documentation_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    result.markdown_path.write_text(
        render_markdown(
            result.config or _config_stub(result),
            result.interpretation_guide,
            result.evidence_usage_policy,
            result.dashboard_reading_guide,
            result.limitations_documentation,
            result.follow_up_plan,
            result.summary,
        ),
        encoding="utf-8",
    )
    return result


def build_report_text(result: ReferenceStabilityDocumentationResult) -> str:
    lines = [
        "SQRE Reference Stability Documentation",
        "======================================",
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
        "Stability Interpretation Guide",
        "------------------------------",
        *_class_count_lines(result.interpretation_guide, "Documentation_Class"),
        "",
        "Evidence Usage Policy",
        "---------------------",
        *_class_count_lines(result.evidence_usage_policy, "Evidence_Usage_Policy_Class"),
        "",
        "Dashboard Reading Guide",
        "-----------------------",
        *_class_count_lines(result.dashboard_reading_guide, "Dashboard_Reading_Guide_Class"),
        "",
        "Limitations Documentation",
        "-------------------------",
        *_category_lines(result.limitations_documentation, "Limitation_Category"),
        "",
        "Follow-Up Plan",
        "--------------",
        *_follow_up_lines(result.follow_up_plan),
        "",
        "Scope Safety Review",
        "-------------------",
        *_class_count_lines(result.scope_safety_review, "Documentation_Scope_Safety_Class"),
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
        "Markdown Output",
        "---------------",
        str(result.markdown_path),
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


def _input_directory_lines(result: ReferenceStabilityDocumentationResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: ReferenceStabilityDocumentationResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:30]]


def _class_count_lines(frame: pd.DataFrame, class_column: str) -> list[str]:
    if frame.empty or class_column not in frame.columns:
        return ["No rows were produced."]
    counts = frame[class_column].value_counts().sort_index()
    return [f"- {name}: {count}" for name, count in counts.items()]


def _category_lines(frame: pd.DataFrame, column: str) -> list[str]:
    if frame.empty or column not in frame.columns:
        return ["No rows were produced."]
    return [f"- {value}" for value in frame[column].astype(str).tolist()]


def _follow_up_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No follow-up rows were produced."]
    return [
        f"- {row.get('Follow_Up_Category')}: {row.get('Follow_Up_Priority')}"
        for _, row in frame.iterrows()
    ]


def _summary_lines(result: ReferenceStabilityDocumentationResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Stability dimension count: {summary.stability_dimension_count}",
        f"Documented stable evidence count: {summary.documented_stable_evidence_count}",
        f"Documented partial evidence count: {summary.documented_partial_evidence_count}",
        f"Documented constrained evidence count: {summary.documented_constrained_evidence_count}",
        f"Documented unstable evidence count: {summary.documented_unstable_evidence_count}",
        f"Safe for manual research review count: {summary.safe_for_manual_research_review_count}",
        f"Use with stability warnings count: {summary.use_with_stability_warnings_count}",
        f"Documentation-only count: {summary.documentation_only_count}",
        f"Dashboard guide element count: {summary.dashboard_guide_element_count}",
        f"Limitation count: {summary.limitation_count}",
        f"Follow-up count: {summary.follow_up_count}",
        f"Scope safety class: {summary.documentation_scope_safety_class}",
        f"Scope warning count: {summary.scope_warning_count}",
        f"Scope violation count: {summary.scope_violation_count}",
        f"Readiness class: {summary.reference_stability_documentation_readiness_class}",
        f"Readiness flag: {summary.reference_stability_documentation_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def _config_stub(result: ReferenceStabilityDocumentationResult):
    from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig

    summary = result.summary
    return ReferenceStabilityDocumentationConfig(
        output_dir=result.output_dir,
        report_path=result.report_path,
        markdown_path=result.markdown_path,
        symbol=summary.symbol if summary else "EURUSD",
        h4_timeframe=summary.h4_timeframe if summary else "H4",
        d1_timeframe=summary.d1_timeframe if summary else "D1",
    )
