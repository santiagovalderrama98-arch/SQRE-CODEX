"""Output writers for D1 regime context adequacy review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.d1_regime_context_adequacy_review.aggregation_candidate_review import AGGREGATION_CANDIDATE_COLUMNS
from sqre.d1_regime_context_adequacy_review.d1_context_inventory import D1_CONTEXT_INVENTORY_COLUMNS
from sqre.d1_regime_context_adequacy_review.d1_context_sample_adequacy_review import (
    D1_CONTEXT_SAMPLE_ADEQUACY_COLUMNS,
)
from sqre.d1_regime_context_adequacy_review.d1_fragmentation_review import FRAGMENTATION_COLUMNS
from sqre.d1_regime_context_adequacy_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_lines,
)
from sqre.d1_regime_context_adequacy_review.h4_transition_sample_loss_review import SAMPLE_LOSS_COLUMNS
from sqre.d1_regime_context_adequacy_review.models import D1RegimeContextAdequacyResult


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Aligned_H4_Transition_Row_Count",
    "Distinct_H4_Transition_Count",
    "Distinct_D1_Market_State_Count",
    "Distinct_D1_Regime_Count",
    "Context_Profile_Count",
    "Research_Ready_Context_Count",
    "Low_Or_Insufficient_Context_Count",
    "D1_Context_Count",
    "High_Fragmentation_Transition_Count",
    "Extreme_Fragmentation_Transition_Count",
    "High_Sample_Loss_Transition_Count",
    "Extreme_Sample_Loss_Transition_Count",
    "Aggregation_Candidate_Count",
    "Dominant_D1_Context_Adequacy_Class",
    "D1_Regime_Context_Adequacy_Readiness_Flag",
    "D1_Regime_Context_Adequacy_Diagnostic",
    "Recommended_Follow_Up",
]
FORBIDDEN_REPORT_TERMS = [
    "buy",
    "sell",
    "entry",
    "exit",
    "trade signal",
    "trade setup",
    "take profit",
    "stop loss",
    "profitable",
    "opportunity",
    "predicts",
    "optimal",
    "should trade",
]


def write_outputs(result: D1RegimeContextAdequacyResult) -> D1RegimeContextAdequacyResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "d1_regime_context_adequacy_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "d1_context_inventory.csv", result.d1_context_inventory, D1_CONTEXT_INVENTORY_COLUMNS)
    _write_frame(
        result.output_dir / "h4_transition_d1_fragmentation_review.csv",
        result.fragmentation_review,
        FRAGMENTATION_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_transition_sample_loss_review.csv",
        result.sample_loss_review,
        SAMPLE_LOSS_COLUMNS,
    )
    _write_frame(
        result.output_dir / "d1_context_sample_adequacy_review.csv",
        result.d1_context_sample_adequacy_review,
        D1_CONTEXT_SAMPLE_ADEQUACY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "d1_context_aggregation_candidate_review.csv",
        result.aggregation_candidate_review,
        AGGREGATION_CANDIDATE_COLUMNS,
    )
    _write_rows(
        result.output_dir / "d1_regime_context_adequacy_review_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: D1RegimeContextAdequacyResult) -> str:
    lines = [
        "SQRE D1 Regime Context Adequacy Review",
        "======================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Input Directories",
        "-----------------",
        *_input_directories(result),
        "",
        "Output Directory",
        "----------------",
        str(result.output_dir),
        "",
        "Source Inventory",
        "----------------",
        *_row_lines(result.source_inventory, "source_name", "load_status", "diagnostic"),
        "",
        "D1 Context Inventory",
        "--------------------",
        f"Rows produced: {len(result.d1_context_inventory)}",
        "",
        "H4 Transition D1 Fragmentation Review",
        "-------------------------------------",
        f"Rows produced: {len(result.fragmentation_review)}",
        "",
        "H4 Transition Sample Loss Review",
        "--------------------------------",
        f"Rows produced: {len(result.sample_loss_review)}",
        "",
        "D1 Context Sample Adequacy Review",
        "---------------------------------",
        f"Rows produced: {len(result.d1_context_sample_adequacy_review)}",
        "",
        "D1 Context Aggregation Candidate Review",
        "---------------------------------------",
        f"Rows produced: {len(result.aggregation_candidate_review)}",
        "",
        "Readiness Assessment",
        "--------------------",
        *_summary_lines(result),
        *readiness_lines(result.summary),
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
        "- This phase reviews D1 context adequacy only.",
        "- This phase does not perform forward price outcome research.",
        "- This phase does not change D1 regime definitions.",
        "- This phase does not aggregate taxonomy in production.",
        "- This phase does not generate trading signals.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- Later phases may either expand historical data, review D1 context grouping, or run limited outcome research on research-ready contexts.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows if row is not None]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _write_frame(path: Path, frame: pd.DataFrame, columns: list[str]) -> None:
    if frame.empty:
        pd.DataFrame(columns=columns).to_csv(path, index=False)
        return
    frame.reindex(columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _row_lines(rows: list[object], id_field: str, status_field: str, diagnostic_field: str) -> list[str]:
    if not rows:
        return ["No rows were produced."]
    return [f"- {getattr(row, id_field)}: {getattr(row, status_field)}; {getattr(row, diagnostic_field)}" for row in rows[:10]]


def _summary_lines(result: D1RegimeContextAdequacyResult) -> list[str]:
    if result.summary is None:
        return ["No summary was produced."]
    summary = result.summary
    return [
        f"Aligned H4 transition rows: {summary.aligned_h4_transition_row_count}",
        f"Context profiles: {summary.context_profile_count}",
        f"Research-ready contexts: {summary.research_ready_context_count}",
        f"Low or insufficient contexts: {summary.low_or_insufficient_context_count}",
        f"D1 context count: {summary.d1_context_count}",
        f"Aggregation candidates: {summary.aggregation_candidate_count}",
    ]


def _input_directories(result: D1RegimeContextAdequacyResult) -> list[str]:
    if not result.source_inventory:
        return ["No input directories were reviewed."]
    parents = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents]


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains forbidden wording: {blocked}")
