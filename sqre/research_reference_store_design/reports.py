"""Output writers for Research Reference Store Design."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.research_reference_store_design.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.research_reference_store_design.granularity_reference_review import GRANULARITY_COLUMNS
from sqre.research_reference_store_design.horizon_reference_review import HORIZON_COLUMNS
from sqre.research_reference_store_design.models import ResearchReferenceStoreDesignResult
from sqre.research_reference_store_design.reference_candidate_builder import CANDIDATE_COLUMNS
from sqre.research_reference_store_design.reference_exclusion_review import EXCLUSION_COLUMNS
from sqre.research_reference_store_design.reference_store_builder import STORE_COLUMNS


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Outcome_Profile_Count",
    "Reference_Candidate_Count",
    "Included_Reference_Count",
    "Core_Reference_Count",
    "Supporting_Reference_Count",
    "Watchlist_Reference_Count",
    "Excluded_Reference_Count",
    "Excluded_Sample_Constrained_Count",
    "Excluded_High_Dispersion_Count",
    "Excluded_Low_Interpretability_Count",
    "Primary_Reference_Granularity",
    "Primary_Reference_Horizon",
    "Research_Reference_Store_Readiness_Class",
    "Research_Reference_Store_Readiness_Flag",
    "Research_Reference_Store_Diagnostic",
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


def write_outputs(result: ResearchReferenceStoreDesignResult) -> ResearchReferenceStoreDesignResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "research_reference_store_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "research_reference_candidates.csv", result.candidates, CANDIDATE_COLUMNS)
    _write_frame(result.output_dir / "research_reference_store.csv", result.reference_store, STORE_COLUMNS)
    _write_frame(result.output_dir / "research_reference_exclusion_review.csv", result.exclusion_review, EXCLUSION_COLUMNS)
    _write_frame(result.output_dir / "research_reference_granularity_review.csv", result.granularity_review, GRANULARITY_COLUMNS)
    _write_frame(result.output_dir / "research_reference_horizon_review.csv", result.horizon_review, HORIZON_COLUMNS)
    _write_rows(
        result.output_dir / "research_reference_store_design_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: ResearchReferenceStoreDesignResult) -> str:
    summary = result.summary
    lines = [
        "SQRE Research Reference Store Design",
        "====================================",
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
        *_row_lines(result.source_inventory),
        "",
        "Research Reference Candidates",
        "-----------------------------",
        f"Candidate rows: {len(result.candidates)}",
        "",
        "Research Reference Store",
        "------------------------",
        f"Included reference rows: {len(result.reference_store)}",
        "",
        "Reference Exclusion Review",
        "--------------------------",
        f"Excluded and watchlist rows: {len(result.exclusion_review)}",
        "",
        "Granularity Reference Review",
        "----------------------------",
        f"Granularity rows: {len(result.granularity_review)}",
        "",
        "Horizon Reference Review",
        "------------------------",
        f"Horizon rows: {len(result.horizon_review)}",
        "",
        "Readiness Assessment",
        "--------------------",
        *_summary_lines(summary),
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
        "- This phase builds a research-only reference store from interpreted historical outcome profiles.",
        "- This phase does not generate trading signals.",
        "- This phase does not generate operational recommendations.",
        "- This phase does not decide whether a context is favorable or unfavorable.",
        "- This phase does not perform profitability analysis.",
        "- This phase does not create a Decision Engine.",
        "- The reference store is not production decision logic.",
        "- Later phases may review how the reference store could be used by research workflows, "
        "but this phase only designs the research artifact.",
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


def _row_lines(rows: list[object]) -> list[str]:
    if not rows:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in rows[:12]]


def _summary_lines(summary: object | None) -> list[str]:
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Outcome profile count: {summary.outcome_profile_count}",
        f"Reference candidate count: {summary.reference_candidate_count}",
        f"Included reference count: {summary.included_reference_count}",
        f"Core reference count: {summary.core_reference_count}",
        f"Supporting reference count: {summary.supporting_reference_count}",
        f"Watchlist reference count: {summary.watchlist_reference_count}",
        f"Excluded reference count: {summary.excluded_reference_count}",
        f"Primary reference granularity: {summary.primary_reference_granularity}",
        f"Primary reference horizon: {summary.primary_reference_horizon}",
        f"Readiness class: {summary.research_reference_store_readiness_class}",
        f"Readiness flag: {summary.research_reference_store_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def _input_directories(result: ResearchReferenceStoreDesignResult) -> list[str]:
    parents = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains forbidden wording: {blocked}")
