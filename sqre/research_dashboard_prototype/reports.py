"""Output writers for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.research_dashboard_prototype.evidence_panel_builder import EVIDENCE_PANEL_COLUMNS
from sqre.research_dashboard_prototype.fallback_panel_builder import FALLBACK_PANEL_COLUMNS
from sqre.research_dashboard_prototype.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    scope_statements,
)
from sqre.research_dashboard_prototype.html_renderer import render_html
from sqre.research_dashboard_prototype.models import ResearchDashboardPrototypeResult
from sqre.research_dashboard_prototype.reference_panel_builder import REFERENCE_CARD_COLUMNS
from sqre.research_dashboard_prototype.snapshot_panel_builder import SNAPSHOT_PANEL_COLUMNS
from sqre.research_dashboard_prototype.source_inventory import SOURCE_COLUMNS
from sqre.research_dashboard_prototype.behavior_panel_builder import BEHAVIOR_PANEL_COLUMNS
from sqre.research_dashboard_prototype.diagnostic_panel_builder import DIAGNOSTIC_PANEL_COLUMNS


SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Snapshot_Mode",
    "Snapshot_Source",
    "Research_Reference_Count",
    "Snapshot_Query_Count",
    "Snapshot_Result_Count",
    "Snapshot_Reference_Coverage_Ratio",
    "Reference_Card_Count",
    "Evidence_Panel_Row_Count",
    "Behavior_Panel_Row_Count",
    "Fallback_Panel_Row_Count",
    "Diagnostic_Panel_Row_Count",
    "Primary_Snapshot_Query_Match_Level",
    "Primary_Snapshot_Horizon",
    "Dashboard_Readiness_Class",
    "Dashboard_Readiness_Flag",
    "Dashboard_Diagnostic",
    "Recommended_Follow_Up",
]


def write_outputs(result: ResearchDashboardPrototypeResult, dashboard_title: str) -> ResearchDashboardPrototypeResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    result.html_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "research_dashboard_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "research_dashboard_snapshot_panel.csv", result.snapshot_panel, SNAPSHOT_PANEL_COLUMNS)
    _write_frame(result.output_dir / "research_dashboard_reference_cards.csv", result.reference_cards, REFERENCE_CARD_COLUMNS)
    _write_frame(result.output_dir / "research_dashboard_evidence_panel.csv", result.evidence_panel, EVIDENCE_PANEL_COLUMNS)
    _write_frame(result.output_dir / "research_dashboard_behavior_panel.csv", result.behavior_panel, BEHAVIOR_PANEL_COLUMNS)
    _write_frame(result.output_dir / "research_dashboard_fallback_panel.csv", result.fallback_panel, FALLBACK_PANEL_COLUMNS)
    _write_frame(result.output_dir / "research_dashboard_diagnostic_panel.csv", result.diagnostic_panel, DIAGNOSTIC_PANEL_COLUMNS)
    _write_rows(result.output_dir / "research_dashboard_summary.csv", [result.summary] if result.summary else [], SUMMARY_COLUMNS)
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    result.html_path.write_text(render_html(result, dashboard_title), encoding="utf-8")
    return result


def build_report_text(result: ResearchDashboardPrototypeResult) -> str:
    lines = [
        "SQRE Research Dashboard Prototype",
        "=================================",
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
        "Dashboard Snapshot Panel",
        "------------------------",
        *_panel_count_lines(result.snapshot_panel, "Snapshot panel rows"),
        "",
        "Dashboard Reference Cards",
        "-------------------------",
        *_panel_count_lines(result.reference_cards, "Reference card rows"),
        "",
        "Dashboard Evidence Panel",
        "------------------------",
        *_panel_count_lines(result.evidence_panel, "Evidence panel rows"),
        "",
        "Dashboard Behavior Panel",
        "------------------------",
        *_panel_count_lines(result.behavior_panel, "Behavior panel rows"),
        "",
        "Dashboard Fallback Panel",
        "------------------------",
        *_panel_count_lines(result.fallback_panel, "Fallback panel rows"),
        "",
        "Dashboard Diagnostic Panel",
        "--------------------------",
        *_panel_count_lines(result.diagnostic_panel, "Diagnostic panel rows"),
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
        "HTML Output",
        "-----------",
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
    return {column: raw.get(column.lower(), "") for column in columns}


def _input_directory_lines(result: ResearchDashboardPrototypeResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: ResearchDashboardPrototypeResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:25]]


def _panel_count_lines(frame: pd.DataFrame, label: str) -> list[str]:
    if frame.empty:
        return [f"{label}: 0", "Panel status: PANEL_EMPTY"]
    status = frame["Panel_Status"].iloc[0] if "Panel_Status" in frame.columns else "PANEL_READY"
    return [f"{label}: {len(frame)}", f"Panel status: {status}"]


def _summary_lines(result: ResearchDashboardPrototypeResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Snapshot mode: {summary.snapshot_mode}",
        f"Snapshot source: {summary.snapshot_source}",
        f"Research reference count: {summary.research_reference_count}",
        f"Snapshot query count: {summary.snapshot_query_count}",
        f"Snapshot result count: {summary.snapshot_result_count}",
        f"Snapshot reference coverage ratio: {summary.snapshot_reference_coverage_ratio}",
        f"Reference card count: {summary.reference_card_count}",
        f"Evidence panel row count: {summary.evidence_panel_row_count}",
        f"Behavior panel row count: {summary.behavior_panel_row_count}",
        f"Fallback panel row count: {summary.fallback_panel_row_count}",
        f"Diagnostic panel row count: {summary.diagnostic_panel_row_count}",
        f"Primary snapshot query match level: {summary.primary_snapshot_query_match_level}",
        f"Primary snapshot horizon: {summary.primary_snapshot_horizon}",
        f"Dashboard readiness class: {summary.dashboard_readiness_class}",
        f"Dashboard readiness flag: {summary.dashboard_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]
