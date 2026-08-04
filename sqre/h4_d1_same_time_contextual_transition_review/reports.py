"""Output writers for H4/D1 same-time contextual transition review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_same_time_contextual_transition_review.contextual_concentration_review import (
    CONCENTRATION_COLUMNS,
)
from sqre.h4_d1_same_time_contextual_transition_review.contextual_transition_profiler import PROFILE_COLUMNS
from sqre.h4_d1_same_time_contextual_transition_review.d1_context_distribution_review import (
    MARKET_STATE_DISTRIBUTION_COLUMNS,
)
from sqre.h4_d1_same_time_contextual_transition_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_lines,
)
from sqre.h4_d1_same_time_contextual_transition_review.models import (
    H4D1SameTimeContextualTransitionReviewResult,
)
from sqre.h4_d1_same_time_contextual_transition_review.regime_context_review import REGIME_DISTRIBUTION_COLUMNS
from sqre.h4_d1_same_time_contextual_transition_review.sample_adequacy_review import SAMPLE_ADEQUACY_COLUMNS


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
    "Moderate_Context_Count",
    "Low_Sample_Context_Count",
    "Insufficient_Context_Count",
    "D1_Context_Concentrated_Transition_Count",
    "D1_Context_Mixed_Transition_Count",
    "D1_Context_Dispersed_Transition_Count",
    "Dominant_Contextual_Review_Class",
    "H4_D1_Contextual_Transition_Readiness_Flag",
    "H4_D1_Contextual_Transition_Diagnostic",
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


def write_outputs(result: H4D1SameTimeContextualTransitionReviewResult) -> H4D1SameTimeContextualTransitionReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(result.output_dir / "h4_d1_contextual_transition_source_inventory.csv", result.source_inventory, SOURCE_COLUMNS)
    _write_frame(
        result.output_dir / "h4_d1_same_time_contextual_transition_profiles.csv",
        result.contextual_profiles,
        PROFILE_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_transition_d1_market_state_distribution.csv",
        result.market_state_distribution,
        MARKET_STATE_DISTRIBUTION_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_transition_d1_regime_distribution.csv",
        result.regime_distribution,
        REGIME_DISTRIBUTION_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_transition_context_concentration_review.csv",
        result.concentration_review,
        CONCENTRATION_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_context_sample_adequacy_review.csv",
        result.sample_adequacy_review,
        SAMPLE_ADEQUACY_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_same_time_contextual_transition_review_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4D1SameTimeContextualTransitionReviewResult) -> str:
    lines = [
        "SQRE H4/D1 Same-Time Contextual Transition Review",
        "=================================================",
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
        "Same-Time Contextual Transition Profiles",
        "----------------------------------------",
        f"Rows produced: {len(result.contextual_profiles)}",
        "",
        "D1 Market State Distribution Review",
        "-----------------------------------",
        f"Rows produced: {len(result.market_state_distribution)}",
        "",
        "D1 Regime Distribution Review",
        "-----------------------------",
        f"Rows produced: {len(result.regime_distribution)}",
        "",
        "Context Concentration Review",
        "----------------------------",
        f"Rows produced: {len(result.concentration_review)}",
        "",
        "Sample Adequacy Review",
        "----------------------",
        f"Rows produced: {len(result.sample_adequacy_review)}",
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
        "- This phase reviews same-time H4/D1 contextual combinations only.",
        "- This phase does not study forward price outcomes.",
        "- This phase does not generate trading signals.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- This phase prepares context profiles for later outcome research.",
        "- Later phases may evaluate forward price outcomes by aligned context, but this phase does not.",
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


def _summary_lines(result: H4D1SameTimeContextualTransitionReviewResult) -> list[str]:
    if result.summary is None:
        return ["No summary was produced."]
    summary = result.summary
    return [
        f"Aligned H4 transition rows: {summary.aligned_h4_transition_row_count}",
        f"Distinct H4 transitions: {summary.distinct_h4_transition_count}",
        f"Distinct D1 market states: {summary.distinct_d1_market_state_count}",
        f"Distinct D1 regimes: {summary.distinct_d1_regime_count}",
        f"Context profiles: {summary.context_profile_count}",
        f"Research-ready contexts: {summary.research_ready_context_count}",
        f"Low or insufficient contexts: {summary.low_sample_context_count + summary.insufficient_context_count}",
    ]


def _input_directories(result: H4D1SameTimeContextualTransitionReviewResult) -> list[str]:
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
