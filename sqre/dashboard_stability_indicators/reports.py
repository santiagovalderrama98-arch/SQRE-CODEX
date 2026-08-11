"""Output writers for dashboard stability indicators."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.dashboard_stability_indicators.behavior_panel_indicator_builder import BEHAVIOR_PANEL_COLUMNS
from sqre.dashboard_stability_indicators.dashboard_warning_builder import WARNING_SUMMARY_COLUMNS
from sqre.dashboard_stability_indicators.evidence_panel_indicator_builder import EVIDENCE_PANEL_COLUMNS
from sqre.dashboard_stability_indicators.fallback_indicator_builder import FALLBACK_PANEL_COLUMNS
from sqre.dashboard_stability_indicators.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    scope_statements,
)
from sqre.dashboard_stability_indicators.indicator_html_renderer import render_html
from sqre.dashboard_stability_indicators.models import DashboardStabilityIndicatorsResult
from sqre.dashboard_stability_indicators.reference_card_indicator_builder import REFERENCE_CARD_COLUMNS
from sqre.dashboard_stability_indicators.scope_safety_review import SCOPE_SAFETY_COLUMNS
from sqre.dashboard_stability_indicators.source_inventory import SOURCE_COLUMNS
from sqre.dashboard_stability_indicators.stability_indicator_legend_builder import LEGEND_COLUMNS
from sqre.dashboard_stability_indicators.stability_indicator_mapper import INDICATOR_MAP_COLUMNS


SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Stability_Dimension_Count",
    "Reference_Card_Count",
    "Stable_Evidence_Indicator_Count",
    "Partial_Evidence_Indicator_Count",
    "Warning_Evidence_Indicator_Count",
    "Documentation_Only_Indicator_Count",
    "Fallback_Dependent_Indicator_Count",
    "Directionally_Unstable_Indicator_Count",
    "Moderate_Stability_Warning_Count",
    "High_Stability_Warning_Count",
    "Scope_Safety_Class",
    "Scope_Warning_Count",
    "Scope_Violation_Count",
    "Dashboard_Stability_Readiness_Class",
    "Dashboard_Stability_Readiness_Flag",
    "Dashboard_Stability_Diagnostic",
    "Recommended_Follow_Up",
]


def write_outputs(result: DashboardStabilityIndicatorsResult) -> DashboardStabilityIndicatorsResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    result.html_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "dashboard_stability_indicator_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "dashboard_stability_indicator_legend.csv", result.indicator_legend, LEGEND_COLUMNS)
    _write_frame(result.output_dir / "dashboard_stability_indicator_map.csv", result.indicator_map, INDICATOR_MAP_COLUMNS)
    _write_frame(
        result.output_dir / "dashboard_reference_card_stability_indicators.csv",
        result.reference_card_indicators,
        REFERENCE_CARD_COLUMNS,
    )
    _write_frame(result.output_dir / "dashboard_evidence_stability_panel.csv", result.evidence_panel, EVIDENCE_PANEL_COLUMNS)
    _write_frame(result.output_dir / "dashboard_behavior_stability_panel.csv", result.behavior_panel, BEHAVIOR_PANEL_COLUMNS)
    _write_frame(result.output_dir / "dashboard_fallback_stability_panel.csv", result.fallback_panel, FALLBACK_PANEL_COLUMNS)
    _write_frame(result.output_dir / "dashboard_stability_warning_summary.csv", result.warning_summary, WARNING_SUMMARY_COLUMNS)
    _write_frame(result.output_dir / "dashboard_stability_scope_safety_review.csv", result.scope_safety_review, SCOPE_SAFETY_COLUMNS)
    _write_rows(
        result.output_dir / "dashboard_stability_indicators_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    config = result.config
    if config is not None:
        result.html_path.write_text(
            render_html(
                config,
                result.summary,
                result.indicator_legend,
                result.reference_card_indicators,
                result.evidence_panel,
                result.behavior_panel,
                result.fallback_panel,
                result.warning_summary,
            ),
            encoding="utf-8",
        )
    return result


def build_report_text(result: DashboardStabilityIndicatorsResult) -> str:
    lines = [
        "SQRE Dashboard Stability Indicators",
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
        "Stability Indicator Legend",
        "--------------------------",
        *_class_count_lines(result.indicator_legend, "Dashboard_Stability_Indicator_Class"),
        "",
        "Stability Indicator Map",
        "-----------------------",
        *_class_count_lines(result.indicator_map, "Dashboard_Stability_Indicator_Class"),
        "",
        "Reference Card Stability Indicators",
        "-----------------------------------",
        *_class_count_lines(result.reference_card_indicators, "Reference_Card_Stability_Class"),
        "",
        "Evidence Stability Panel",
        "------------------------",
        *_class_count_lines(result.evidence_panel, "Dashboard_Stability_Indicator_Class"),
        "",
        "Behavior Stability Panel",
        "------------------------",
        *_class_count_lines(result.behavior_panel, "Dashboard_Stability_Indicator_Class"),
        "",
        "Fallback Stability Panel",
        "------------------------",
        *_class_count_lines(result.fallback_panel, "Dashboard_Warning_Class"),
        "",
        "Warning Summary",
        "---------------",
        *_warning_lines(result.warning_summary),
        "",
        "Scope Safety Review",
        "-------------------",
        *_class_count_lines(result.scope_safety_review, "Dashboard_Stability_Scope_Safety_Class"),
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
    return {column: raw.get(_snake(column), "") for column in columns}


def _snake(name: str) -> str:
    out = []
    for index, char in enumerate(name):
        if char.isupper() and index > 0 and name[index - 1] != "_":
            out.append("_")
        out.append(char.lower())
    return "".join(out)


def _input_directory_lines(result: DashboardStabilityIndicatorsResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: DashboardStabilityIndicatorsResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:40]]


def _class_count_lines(frame: pd.DataFrame, class_column: str) -> list[str]:
    if frame.empty or class_column not in frame.columns:
        return ["No rows were produced."]
    counts = frame[class_column].value_counts().sort_index()
    return [f"- {name}: {count}" for name, count in counts.items()]


def _warning_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No warning rows were produced."]
    return [
        f"- {row.get('Dashboard_Warning_Class')}: {row.get('Warning_Count')} warning row(s); severity={row.get('Dashboard_Stability_Severity_Class')}"
        for _, row in frame.iterrows()
    ]


def _summary_lines(result: DashboardStabilityIndicatorsResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Stability dimension count: {summary.stability_dimension_count}",
        f"Reference card count: {summary.reference_card_count}",
        f"Stable evidence indicator count: {summary.stable_evidence_indicator_count}",
        f"Partial evidence indicator count: {summary.partial_evidence_indicator_count}",
        f"Warning evidence indicator count: {summary.warning_evidence_indicator_count}",
        f"Documentation-only indicator count: {summary.documentation_only_indicator_count}",
        f"Fallback-dependent indicator count: {summary.fallback_dependent_indicator_count}",
        f"Directionally unstable indicator count: {summary.directionally_unstable_indicator_count}",
        f"Moderate stability warning count: {summary.moderate_stability_warning_count}",
        f"High stability warning count: {summary.high_stability_warning_count}",
        f"Scope safety class: {summary.scope_safety_class}",
        f"Scope warning count: {summary.scope_warning_count}",
        f"Scope violation count: {summary.scope_violation_count}",
        f"Readiness class: {summary.dashboard_stability_readiness_class}",
        f"Readiness flag: {summary.dashboard_stability_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]
