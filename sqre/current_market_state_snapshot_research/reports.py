"""Output writers for Current Market State Snapshot Research."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.current_market_state_snapshot_research.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.current_market_state_snapshot_research.models import CurrentMarketStateSnapshotResearchResult
from sqre.current_market_state_snapshot_research.snapshot_behavior_summary import SNAPSHOT_BEHAVIOR_SUMMARY_COLUMNS
from sqre.current_market_state_snapshot_research.snapshot_context_builder import SNAPSHOT_CONTEXT_COLUMNS
from sqre.current_market_state_snapshot_research.snapshot_diagnostic_review import SNAPSHOT_DIAGNOSTIC_REVIEW_COLUMNS
from sqre.current_market_state_snapshot_research.snapshot_evidence_review import SNAPSHOT_EVIDENCE_REVIEW_COLUMNS
from sqre.current_market_state_snapshot_research.snapshot_query_builder import SNAPSHOT_QUERY_COLUMNS
from sqre.current_market_state_snapshot_research.snapshot_reference_lookup import (
    SNAPSHOT_FALLBACK_TRACE_COLUMNS,
    SNAPSHOT_REFERENCE_RESULT_COLUMNS,
)


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Snapshot_Mode",
    "Snapshot_Source",
    "Snapshot_Timestamp",
    "Snapshot_Timestamp_Status",
    "Snapshot_Validation_Status",
    "Research_Reference_Count",
    "Snapshot_Query_Count",
    "Snapshot_Result_Count",
    "Snapshot_Query_With_Result_Count",
    "Snapshot_Query_Without_Result_Count",
    "Snapshot_Reference_Coverage_Ratio",
    "High_Evidence_Snapshot_Result_Count",
    "Moderate_Evidence_Snapshot_Result_Count",
    "Low_Evidence_Snapshot_Result_Count",
    "No_Usable_Snapshot_Result_Count",
    "Core_Evidence_Snapshot_Result_Count",
    "Supporting_Evidence_Snapshot_Result_Count",
    "Primary_Snapshot_Query_Match_Level",
    "Primary_Snapshot_Horizon",
    "Dominant_Current_Market_State_Snapshot_Readiness_Class",
    "Current_Market_State_Snapshot_Readiness_Flag",
    "Current_Market_State_Snapshot_Diagnostic",
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


def write_outputs(result: CurrentMarketStateSnapshotResearchResult) -> CurrentMarketStateSnapshotResearchResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(
        result.output_dir / "current_market_state_snapshot_source_inventory.csv",
        result.source_inventory,
        SOURCE_COLUMNS,
    )
    _write_frame(result.output_dir / "current_market_state_snapshot_context.csv", result.snapshot_context, SNAPSHOT_CONTEXT_COLUMNS)
    _write_frame(
        result.output_dir / "current_market_state_snapshot_query_requests.csv",
        result.snapshot_query_requests,
        SNAPSHOT_QUERY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "current_market_state_snapshot_reference_results.csv",
        result.snapshot_reference_results,
        SNAPSHOT_REFERENCE_RESULT_COLUMNS,
    )
    _write_frame(
        result.output_dir / "current_market_state_snapshot_fallback_trace.csv",
        result.snapshot_fallback_trace,
        SNAPSHOT_FALLBACK_TRACE_COLUMNS,
    )
    _write_frame(
        result.output_dir / "current_market_state_snapshot_evidence_review.csv",
        result.snapshot_evidence_review,
        SNAPSHOT_EVIDENCE_REVIEW_COLUMNS,
    )
    _write_frame(
        result.output_dir / "current_market_state_snapshot_behavior_summary.csv",
        result.snapshot_behavior_summary,
        SNAPSHOT_BEHAVIOR_SUMMARY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "current_market_state_snapshot_diagnostic_review.csv",
        result.snapshot_diagnostic_review,
        SNAPSHOT_DIAGNOSTIC_REVIEW_COLUMNS,
    )
    _write_rows(
        result.output_dir / "current_market_state_snapshot_research_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    text = build_report_text(result)
    _validate_report_text(text)
    result.report_path.write_text(text, encoding="utf-8")
    return result


def build_report_text(result: CurrentMarketStateSnapshotResearchResult) -> str:
    lines = [
        "SQRE Current Market State Snapshot Research Workflow",
        "====================================================",
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
        "Snapshot Context",
        "----------------",
        *_frame_count_lines(result.snapshot_context, "Snapshot context rows"),
        *_first_row_lines(result.snapshot_context, ["Snapshot_Mode", "Snapshot_Source", "Snapshot_Validation_Status"]),
        "",
        "Snapshot Query Requests",
        "-----------------------",
        *_frame_count_lines(result.snapshot_query_requests, "Snapshot query request rows"),
        "",
        "Snapshot Reference Results",
        "--------------------------",
        *_frame_count_lines(result.snapshot_reference_results, "Snapshot reference result rows"),
        *_match_lines(result.snapshot_reference_results),
        "",
        "Snapshot Fallback Trace",
        "-----------------------",
        *_frame_count_lines(result.snapshot_fallback_trace, "Snapshot fallback trace rows"),
        "",
        "Snapshot Evidence Review",
        "------------------------",
        *_frame_count_lines(result.snapshot_evidence_review, "Snapshot evidence review rows"),
        "",
        "Snapshot Behavior Summary",
        "-------------------------",
        *_frame_count_lines(result.snapshot_behavior_summary, "Snapshot behavior summary rows"),
        "",
        "Snapshot Diagnostic Review",
        "--------------------------",
        *_diagnostic_lines(result.snapshot_diagnostic_review),
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
        "- This phase builds a research-only current or latest-available structural snapshot workflow.",
        "- Latest available snapshot mode depends on local research files and is not live market data unless explicitly connected in a later phase.",
        "- This phase retrieves descriptive historical references for the snapshot context.",
        "- This phase does not generate trading signals.",
        "- This phase does not generate operational recommendations.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- This phase does not perform profitability analysis.",
        "- This phase does not create a Decision Engine.",
        "- Snapshot reference results are descriptive historical references only.",
        "- Later phases may design dashboard visualization or live data integration, but this phase does not create production decision logic.",
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


def _input_directory_lines(result: CurrentMarketStateSnapshotResearchResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: CurrentMarketStateSnapshotResearchResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:25]]


def _frame_count_lines(frame: pd.DataFrame, label: str) -> list[str]:
    return [f"{label}: {len(frame)}"]


def _first_row_lines(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    if frame.empty:
        return ["No row was produced."]
    row = frame.iloc[0]
    return [f"{column}: {row.get(column, '')}" for column in columns]


def _match_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No result rows were produced."]
    return [f"- {level}: {count}" for level, count in frame["Snapshot_Query_Match_Level"].value_counts().to_dict().items()]


def _diagnostic_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No diagnostic rows were produced."]
    return [f"- {row.Diagnostic_Category}: {row.Diagnostic_Status}; {row.Diagnostic_Message}" for row in frame.itertuples()]


def _summary_lines(result: CurrentMarketStateSnapshotResearchResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Snapshot mode: {summary.snapshot_mode}",
        f"Snapshot source: {summary.snapshot_source}",
        f"Research reference count: {summary.research_reference_count}",
        f"Snapshot query count: {summary.snapshot_query_count}",
        f"Snapshot result count: {summary.snapshot_result_count}",
        f"Snapshot query with result count: {summary.snapshot_query_with_result_count}",
        f"Snapshot query without result count: {summary.snapshot_query_without_result_count}",
        f"Snapshot reference coverage ratio: {summary.snapshot_reference_coverage_ratio}",
        f"Primary snapshot query match level: {summary.primary_snapshot_query_match_level}",
        f"Primary snapshot horizon: {summary.primary_snapshot_horizon}",
        f"Readiness class: {summary.dominant_current_market_state_snapshot_readiness_class}",
        f"Readiness flag: {summary.current_market_state_snapshot_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    violations = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if violations:
        raise ValueError(f"Report includes forbidden operational language: {violations}")
