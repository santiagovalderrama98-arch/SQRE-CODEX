"""Output writers for Research Reference Store Usage Review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.research_reference_store_usage_review.evidence_quality_review import EVIDENCE_QUALITY_COLUMNS
from sqre.research_reference_store_usage_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)
from sqre.research_reference_store_usage_review.granularity_usage_review import GRANULARITY_USAGE_COLUMNS
from sqre.research_reference_store_usage_review.horizon_usage_review import HORIZON_USAGE_COLUMNS
from sqre.research_reference_store_usage_review.models import ResearchReferenceStoreUsageReviewResult
from sqre.research_reference_store_usage_review.reference_availability_review import AVAILABILITY_COLUMNS
from sqre.research_reference_store_usage_review.reference_lookup_engine import LOOKUP_COLUMNS
from sqre.research_reference_store_usage_review.usage_scenario_builder import SCENARIO_COLUMNS


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Research_Reference_Count",
    "Usage_Scenario_Count",
    "Matched_Scenario_Count",
    "Unmatched_Scenario_Count",
    "Reference_Availability_Ratio",
    "High_Quality_Match_Count",
    "Moderate_Quality_Match_Count",
    "Low_Quality_Match_Count",
    "No_Usable_Match_Count",
    "Core_Evidence_Match_Count",
    "Supporting_Evidence_Match_Count",
    "Primary_Usage_Granularity",
    "Primary_Usage_Horizon",
    "Dominant_Reference_Usage_Readiness_Class",
    "Research_Reference_Store_Usage_Readiness_Flag",
    "Research_Reference_Store_Usage_Diagnostic",
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


def write_outputs(result: ResearchReferenceStoreUsageReviewResult) -> ResearchReferenceStoreUsageReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "research_reference_store_usage_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(result.output_dir / "research_reference_usage_scenarios.csv", result.usage_scenarios, SCENARIO_COLUMNS)
    _write_frame(result.output_dir / "research_reference_lookup_results.csv", result.lookup_results, LOOKUP_COLUMNS)
    _write_frame(result.output_dir / "research_reference_availability_review.csv", result.availability_review, AVAILABILITY_COLUMNS)
    _write_frame(
        result.output_dir / "research_reference_granularity_usage_review.csv",
        result.granularity_usage_review,
        GRANULARITY_USAGE_COLUMNS,
    )
    _write_frame(result.output_dir / "research_reference_horizon_usage_review.csv", result.horizon_usage_review, HORIZON_USAGE_COLUMNS)
    _write_frame(
        result.output_dir / "research_reference_evidence_quality_review.csv",
        result.evidence_quality_review,
        EVIDENCE_QUALITY_COLUMNS,
    )
    _write_rows(
        result.output_dir / "research_reference_store_usage_review_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: ResearchReferenceStoreUsageReviewResult) -> str:
    lines = [
        "SQRE Research Reference Store Usage Review",
        "==========================================",
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
        *_source_lines(result),
        "",
        "Usage Scenario Generation",
        "-------------------------",
        f"Usage scenario rows: {len(result.usage_scenarios)}",
        "",
        "Reference Lookup Results",
        "------------------------",
        f"Lookup rows: {len(result.lookup_results)}",
        *_match_lines(result.lookup_results),
        "",
        "Reference Availability Review",
        "-----------------------------",
        *_first_row_lines(result.availability_review, ["Reference_Availability_Ratio", "Reference_Availability_Class"]),
        "",
        "Granularity Usage Review",
        "------------------------",
        f"Granularity usage rows: {len(result.granularity_usage_review)}",
        "",
        "Horizon Usage Review",
        "--------------------",
        f"Horizon usage rows: {len(result.horizon_usage_review)}",
        "",
        "Evidence Quality Review",
        "-----------------------",
        f"Evidence quality rows: {len(result.evidence_quality_review)}",
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
        "- This phase reviews how the research reference store can be queried by research workflows.",
        "- This phase does not generate trading signals.",
        "- This phase does not generate operational recommendations.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- This phase does not perform profitability analysis.",
        "- This phase does not create a Decision Engine.",
        "- Reference lookup results are descriptive historical references only.",
        "- Later phases may design a research query interface, but this phase does not create production decision logic.",
    ]
    return "\n".join(lines) + "\n"


def _write_rows(path: Path, rows: list[object], columns: list[str]) -> None:
    records = [_record(row, columns) for row in rows if row is not None]
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _write_frame(path: Path, frame: pd.DataFrame, columns: list[str]) -> None:
    if frame.empty:
        pd.DataFrame(columns=columns).to_csv(path, index=False)
    else:
        frame.reindex(columns=columns).to_csv(path, index=False)


def _record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(column.lower(), "") for column in columns}


def _input_directories(result: ResearchReferenceStoreUsageReviewResult) -> list[str]:
    parents = []
    for row in result.source_inventory:
        parent = str(Path(row.path).parent)
        if parent not in parents:
            parents.append(parent)
    return [f"- {parent}" for parent in parents] if parents else ["No input directories were reviewed."]


def _source_lines(result: ResearchReferenceStoreUsageReviewResult) -> list[str]:
    if not result.source_inventory:
        return ["No source rows were produced."]
    return [f"- {row.source_name}: {row.load_status}; {row.diagnostic}" for row in result.source_inventory[:15]]


def _match_lines(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return ["No lookup rows were produced."]
    return [f"- {level}: {count}" for level, count in frame["Reference_Match_Level"].value_counts().to_dict().items()]


def _first_row_lines(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    if frame.empty:
        return ["No review rows were produced."]
    row = frame.iloc[0]
    return [f"{column}: {row.get(column, '')}" for column in columns]


def _summary_lines(result: ResearchReferenceStoreUsageReviewResult) -> list[str]:
    summary = result.summary
    if summary is None:
        return ["No summary was produced."]
    return [
        f"Research reference count: {summary.research_reference_count}",
        f"Usage scenario count: {summary.usage_scenario_count}",
        f"Matched scenario count: {summary.matched_scenario_count}",
        f"Unmatched scenario count: {summary.unmatched_scenario_count}",
        f"Reference availability ratio: {summary.reference_availability_ratio}",
        f"High quality match count: {summary.high_quality_match_count}",
        f"Moderate quality match count: {summary.moderate_quality_match_count}",
        f"Low quality match count: {summary.low_quality_match_count}",
        f"No usable match count: {summary.no_usable_match_count}",
        f"Core evidence match count: {summary.core_evidence_match_count}",
        f"Supporting evidence match count: {summary.supporting_evidence_match_count}",
        f"Primary usage granularity: {summary.primary_usage_granularity}",
        f"Primary usage horizon: {summary.primary_usage_horizon}",
        f"Readiness class: {summary.dominant_reference_usage_readiness_class}",
        f"Readiness flag: {summary.research_reference_store_usage_readiness_flag}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def _validate_report_text(text: str) -> None:
    lowered = text.lower()
    blocked = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if blocked:
        raise ValueError(f"Report contains forbidden wording: {blocked}")
