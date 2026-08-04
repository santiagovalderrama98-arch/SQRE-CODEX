"""Output writers for Research Query Interface Design."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.research_query_interface_design.findings import do_not_change_yet_lines, limitation_lines, potential_follow_up_areas
from sqre.research_query_interface_design.models import ResearchQueryInterfaceDesignResult
from sqre.research_query_interface_design.query_coverage_review import COVERAGE_COLUMNS
from sqre.research_query_interface_design.query_fallback_engine import TRACE_COLUMNS
from sqre.research_query_interface_design.query_request_builder import REQUEST_COLUMNS
from sqre.research_query_interface_design.query_result_quality_review import EVIDENCE_QUALITY_COLUMNS, RESULT_QUALITY_COLUMNS
from sqre.research_query_interface_design.research_query_engine import RESULT_COLUMNS


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Research_Reference_Count",
    "Research_Query_Request_Count",
    "Valid_Query_Request_Count",
    "Query_Result_Count",
    "Query_With_Result_Count",
    "Query_Without_Result_Count",
    "Research_Query_Coverage_Ratio",
    "High_Quality_Query_Result_Count",
    "Moderate_Quality_Query_Result_Count",
    "Low_Quality_Query_Result_Count",
    "No_Usable_Query_Result_Count",
    "Core_Evidence_Query_Result_Count",
    "Supporting_Evidence_Query_Result_Count",
    "Primary_Query_Match_Level",
    "Primary_Query_Horizon",
    "Dominant_Research_Query_Interface_Readiness_Class",
    "Research_Query_Interface_Readiness_Flag",
    "Research_Query_Interface_Diagnostic",
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


def write_outputs(result: ResearchQueryInterfaceDesignResult) -> ResearchQueryInterfaceDesignResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "research_query_interface_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "research_query_requests.csv", result.query_requests, REQUEST_COLUMNS)
    _write_frame(result.output_dir / "research_query_results.csv", result.query_results, RESULT_COLUMNS)
    _write_frame(result.output_dir / "research_query_fallback_trace.csv", result.fallback_trace, TRACE_COLUMNS)
    _write_frame(result.output_dir / "research_query_evidence_quality_review.csv", result.evidence_quality_review, EVIDENCE_QUALITY_COLUMNS)
    _write_frame(result.output_dir / "research_query_coverage_review.csv", result.coverage_review, COVERAGE_COLUMNS)
    _write_frame(result.output_dir / "research_query_result_quality_review.csv", result.result_quality_review, RESULT_QUALITY_COLUMNS)
    _write_rows(
        result.output_dir / "research_query_interface_design_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    text = build_report_text(result)
    _validate_report_text(text)
    result.report_path.write_text(text, encoding="utf-8")
    return result


def build_report_text(result: ResearchQueryInterfaceDesignResult) -> str:
    lines = [
        "SQRE Research Query Interface Design",
        "====================================",
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
        "Research Query Requests",
        "-----------------------",
        f"Request rows: {len(result.query_requests)}",
        "",
        "Research Query Results",
        "----------------------",
        f"Result rows: {len(result.query_results)}",
        *_match_lines(result.query_results),
        "",
        "Query Fallback Trace",
        "--------------------",
        f"Fallback trace rows: {len(result.fallback_trace)}",
        "",
        "Query Evidence Quality Review",
        "-----------------------------",
        f"Evidence quality rows: {len(result.evidence_quality_review)}",
        "",
        "Query Coverage Review",
        "---------------------",
        *_first_row_lines(result.coverage_review, ["Research_Query_Coverage_Ratio", "Research_Query_Coverage_Class"]),
        "",
        "Query Result Quality Review",
        "---------------------------",
        f"Result quality rows: {len(result.result_quality_review)}",
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
        "- This phase designs a research-only query interface.",
        "- This phase retrieves descriptive historical references for supplied or simulated structural contexts.",
        "- This phase does not generate trading signals.",
        "- This phase does not generate operational recommendations.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- This phase does not perform profitability analysis.",
        "- This phase does not create a Decision Engine.",
        "- Query results are descriptive historical references only.",
        "- Later phases may design a current market state snapshot research workflow, but this phase does not create production decision logic.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows if row is not None]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _write_frame(path: Path, frame: pd.DataFrame, columns: list[str]) -> None:
    pd.DataFrame(columns=columns if frame.empty else frame.reindex(columns=columns).columns).to_csv(path, index=False) if frame.empty else frame.reindex(columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _input_directory_lines(result: ResearchQueryInterfaceDesignResult) -> list[str]:
    parents: list[str] = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: ResearchQueryInterfaceDesignResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:20]]


def _match_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No result rows were produced."]
    return [f"- {level}: {count}" for level, count in frame["Research_Query_Match_Level"].value_counts().to_dict().items()]


def _first_row_lines(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    if frame.empty:
        return ["No review rows were produced."]
    row = frame.iloc[0]
    return [f"{column}: {row.get(column, '')}" for column in columns]


def _summary_lines(result: ResearchQueryInterfaceDesignResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Research reference count: {summary.research_reference_count}",
        f"Research query request count: {summary.research_query_request_count}",
        f"Query result count: {summary.query_result_count}",
        f"Query with result count: {summary.query_with_result_count}",
        f"Query without result count: {summary.query_without_result_count}",
        f"Research query coverage ratio: {summary.research_query_coverage_ratio}",
        f"Primary query match level: {summary.primary_query_match_level}",
        f"Primary query horizon: {summary.primary_query_horizon}",
        f"Readiness class: {summary.dominant_research_query_interface_readiness_class}",
        f"Readiness flag: {summary.research_query_interface_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains forbidden wording: {blocked}")

