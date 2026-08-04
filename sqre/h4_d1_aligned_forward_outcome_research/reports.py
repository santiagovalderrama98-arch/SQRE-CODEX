"""Output writers for H4/D1 aligned forward outcome research."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_lines,
)
from sqre.h4_d1_aligned_forward_outcome_research.forward_outcome_calculator import FORWARD_OUTCOME_COLUMNS
from sqre.h4_d1_aligned_forward_outcome_research.models import H4D1AlignedForwardOutcomeResearchResult
from sqre.h4_d1_aligned_forward_outcome_research.outcome_dispersion_review import DISPERSION_REVIEW_COLUMNS
from sqre.h4_d1_aligned_forward_outcome_research.outcome_profile_builder import OUTCOME_PROFILE_COLUMNS
from sqre.h4_d1_aligned_forward_outcome_research.sample_adequacy_review import SAMPLE_ADEQUACY_REVIEW_COLUMNS


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Aligned_H4_Transition_Row_Count",
    "Forward_Outcome_Row_Count",
    "Complete_Forward_Outcome_Row_Count",
    "Partial_Forward_Outcome_Row_Count",
    "Missing_Forward_Outcome_Row_Count",
    "Outcome_Profile_Count",
    "Research_Ready_Outcome_Profile_Count",
    "Moderate_Outcome_Profile_Count",
    "Low_Or_Insufficient_Outcome_Profile_Count",
    "H4_Transition_Only_Profile_Count",
    "H4_Transition_D1_Market_State_Profile_Count",
    "H4_Transition_D1_Regime_Profile_Count",
    "H4_Transition_D1_State_Regime_Profile_Count",
    "Dominant_Outcome_Readiness_Class",
    "H4_D1_Aligned_Forward_Outcome_Readiness_Flag",
    "H4_D1_Aligned_Forward_Outcome_Diagnostic",
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


def write_outputs(result: H4D1AlignedForwardOutcomeResearchResult) -> H4D1AlignedForwardOutcomeResearchResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(
        result.output_dir / "h4_d1_aligned_forward_outcome_source_inventory.csv",
        result.source_inventory,
        SOURCE_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_transition_forward_outcomes.csv",
        result.forward_outcomes,
        FORWARD_OUTCOME_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_forward_outcome_profiles.csv",
        result.outcome_profiles,
        OUTCOME_PROFILE_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_forward_outcome_dispersion_review.csv",
        result.dispersion_review,
        DISPERSION_REVIEW_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_forward_outcome_sample_adequacy_review.csv",
        result.sample_adequacy_review,
        SAMPLE_ADEQUACY_REVIEW_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_aligned_forward_outcome_research_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4D1AlignedForwardOutcomeResearchResult) -> str:
    lines = [
        "SQRE H4/D1 Aligned Forward Outcome Research",
        "===========================================",
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
        "Forward Outcome Calculation",
        "---------------------------",
        f"Aligned H4 transition rows: {len(result.transition_alignment)}",
        f"Forward outcome rows: {len(result.forward_outcomes)}",
        "",
        "Context Granularity Outcome Profiles",
        "------------------------------------",
        f"Outcome profile rows: {len(result.outcome_profiles)}",
        "Granularity levels: H4 transition only; H4 transition plus D1 market state; "
        "H4 transition plus D1 regime; H4 transition plus D1 state and regime.",
        "",
        "Outcome Dispersion Review",
        "-------------------------",
        f"Dispersion rows: {len(result.dispersion_review)}",
        "",
        "Outcome Sample Adequacy Review",
        "------------------------------",
        f"Sample adequacy rows: {len(result.sample_adequacy_review)}",
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
        "- This phase measures historical forward price behavior after aligned H4 transitions.",
        "- This phase uses multiple context granularities to avoid relying only on over-fragmented D1 context.",
        "- This phase does not generate trading signals.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- This phase does not perform profitability analysis.",
        "- This phase does not create a Decision Engine.",
        "- Later phases may interpret outcome profiles, but this phase only measures them.",
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


def _summary_lines(result: H4D1AlignedForwardOutcomeResearchResult) -> list[str]:
    if result.summary is None:
        return ["No summary was produced."]
    summary = result.summary
    return [
        f"Complete forward outcome rows: {summary.complete_forward_outcome_row_count}",
        f"Partial forward outcome rows: {summary.partial_forward_outcome_row_count}",
        f"Missing forward outcome rows: {summary.missing_forward_outcome_row_count}",
        f"Research-ready outcome profiles: {summary.research_ready_outcome_profile_count}",
        f"Moderate outcome profiles: {summary.moderate_outcome_profile_count}",
        f"Low or insufficient outcome profiles: {summary.low_or_insufficient_outcome_profile_count}",
    ]


def _input_directories(result: H4D1AlignedForwardOutcomeResearchResult) -> list[str]:
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
