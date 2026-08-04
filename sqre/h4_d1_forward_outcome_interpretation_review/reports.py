"""Output writers for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.context_granularity_review import GRANULARITY_COLUMNS
from sqre.h4_d1_forward_outcome_interpretation_review.directional_behavior_review import DIRECTIONAL_COLUMNS
from sqre.h4_d1_forward_outcome_interpretation_review.excursion_behavior_review import EXCURSION_COLUMNS
from sqre.h4_d1_forward_outcome_interpretation_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
    readiness_lines,
)
from sqre.h4_d1_forward_outcome_interpretation_review.horizon_stability_review import HORIZON_STABILITY_COLUMNS
from sqre.h4_d1_forward_outcome_interpretation_review.models import (
    H4D1ForwardOutcomeInterpretationReviewResult,
)
from sqre.h4_d1_forward_outcome_interpretation_review.profile_interpretability_review import INTERPRETABILITY_COLUMNS


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]
SUMMARY_COLUMNS = [
    "Symbol",
    "H4_Timeframe",
    "D1_Timeframe",
    "Outcome_Profile_Count",
    "Interpretable_Profile_Count",
    "Moderately_Interpretable_Profile_Count",
    "Low_Interpretability_Profile_Count",
    "Sample_Constrained_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Upward_Dominance_Profile_Count",
    "Downward_Dominance_Profile_Count",
    "Mixed_Behavior_Profile_Count",
    "Stable_Horizon_Context_Count",
    "Unstable_Horizon_Context_Count",
    "Best_Supported_Context_Granularity",
    "Dominant_Interpretation_Readiness_Class",
    "H4_D1_Forward_Outcome_Interpretation_Readiness_Flag",
    "H4_D1_Forward_Outcome_Interpretation_Diagnostic",
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


def write_outputs(
    result: H4D1ForwardOutcomeInterpretationReviewResult,
) -> H4D1ForwardOutcomeInterpretationReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_rows(
        result.output_dir / "h4_d1_forward_outcome_interpretation_source_inventory.csv",
        result.source_inventory,
        SOURCE_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_outcome_profile_interpretability_review.csv",
        result.interpretability_review,
        INTERPRETABILITY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_directional_behavior_review.csv",
        result.directional_behavior_review,
        DIRECTIONAL_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_excursion_behavior_review.csv",
        result.excursion_behavior_review,
        EXCURSION_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_horizon_stability_review.csv",
        result.horizon_stability_review,
        HORIZON_STABILITY_COLUMNS,
    )
    _write_frame(
        result.output_dir / "h4_d1_context_granularity_utility_review.csv",
        result.context_granularity_review,
        GRANULARITY_COLUMNS,
    )
    _write_rows(
        result.output_dir / "h4_d1_forward_outcome_interpretation_review_summary.csv",
        [result.summary] if result.summary else [],
        SUMMARY_COLUMNS,
    )
    report_text = build_report_text(result)
    _validate_report_text(report_text)
    result.report_path.write_text(report_text, encoding="utf-8")
    return result


def build_report_text(result: H4D1ForwardOutcomeInterpretationReviewResult) -> str:
    lines = [
        "SQRE H4/D1 Forward Outcome Interpretation Review",
        "================================================",
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
        "Outcome Profile Interpretability Review",
        "---------------------------------------",
        f"Outcome profile rows: {len(result.interpretability_review)}",
        "",
        "Directional Behavior Review",
        "---------------------------",
        f"Directional behavior rows: {len(result.directional_behavior_review)}",
        "",
        "Excursion Behavior Review",
        "-------------------------",
        f"Excursion behavior rows: {len(result.excursion_behavior_review)}",
        "",
        "Horizon Stability Review",
        "------------------------",
        f"Horizon stability rows: {len(result.horizon_stability_review)}",
        "",
        "Context Granularity Utility Review",
        "----------------------------------",
        f"Context granularity rows: {len(result.context_granularity_review)}",
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
        "- This phase interprets historical forward outcome profiles descriptively.",
        "- This phase does not generate trading signals.",
        "- This phase does not decide whether any context is favorable or unfavorable.",
        "- This phase does not perform profitability analysis.",
        "- This phase does not create a Decision Engine.",
        "- This phase does not produce operational recommendations.",
        "- Later phases may store research-ready profiles in a research reference store, "
        "but this phase does not create production decision logic.",
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


def _summary_lines(result: H4D1ForwardOutcomeInterpretationReviewResult) -> list[str]:
    if result.summary is None:
        return ["No summary was produced."]
    summary = result.summary
    return [
        f"Outcome profile count: {summary.outcome_profile_count}",
        f"Interpretable profile count: {summary.interpretable_profile_count}",
        f"Moderately interpretable profile count: {summary.moderately_interpretable_profile_count}",
        f"Sample-constrained profile count: {summary.sample_constrained_profile_count}",
        f"High-dispersion profile count: {summary.high_dispersion_profile_count}",
        f"Best-supported context granularity: {summary.best_supported_context_granularity}",
    ]


def _input_directories(result: H4D1ForwardOutcomeInterpretationReviewResult) -> list[str]:
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
