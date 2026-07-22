"""Load Phase 7.5.11 partial sample outputs."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)
from sqre.h4_partial_complementary_dispersion_review.loader import (
    first_row,
    int_value,
    number_value,
    read_optional_csv,
    text_value,
)
from sqre.h4_partial_complementary_dispersion_review.models import (
    PartialSampleReviewRow,
    PartialStructureStateSnapshot,
    PartialTransitionSnapshot,
)


def load_partial_sample_review(
    config: H4PartialComplementaryDispersionReviewConfig,
) -> list[PartialSampleReviewRow]:
    candidate_frame = read_optional_csv(config.partial_validation_dir / "h4_partial_candidate_inventory.csv")
    run_frame = read_optional_csv(config.partial_validation_dir / "h4_partial_validation_run_summary.csv")
    adequacy_frame = read_optional_csv(config.partial_validation_dir / "h4_partial_sample_adequacy_review.csv")
    comparison_frame = read_optional_csv(config.partial_validation_dir / "h4_partial_vs_baseline_comparison.csv")
    summary_frame = read_optional_csv(
        config.partial_validation_dir / "h4_targeted_partial_expansion_validation_summary.csv"
    )

    candidate_row = _candidate_or_first(candidate_frame, config.candidate_id)
    run_row = _candidate_or_first(run_frame, config.candidate_id)
    adequacy_row = _candidate_or_first(adequacy_frame, config.candidate_id)
    comparison_row = _candidate_or_first(comparison_frame, config.candidate_id)
    summary_row = first_row(summary_frame)

    if candidate_row is None and run_row is None and adequacy_row is None and comparison_row is None:
        return []

    candidate_id = _first_text(
        [
            (candidate_row, ["Candidate_ID", "candidate_id"]),
            (run_row, ["Candidate_ID", "candidate_id"]),
            (adequacy_row, ["Candidate_ID", "candidate_id"]),
            (comparison_row, ["Candidate_ID", "candidate_id"]),
        ],
        config.candidate_id,
    )
    sample_label = _first_text(
        [
            (candidate_row, ["Sample_Label", "sample_label"]),
            (run_row, ["Sample_Label", "sample_label"]),
            (adequacy_row, ["Sample_Label", "sample_label"]),
            (comparison_row, ["Sample_Label", "sample_label"]),
        ],
        config.partial_sample_label,
    )
    coverage_ratio = _first_number(
        [
            (candidate_row, ["Coverage_Ratio", "coverage_ratio"]),
            (adequacy_row, ["Coverage_Ratio", "coverage_ratio"]),
            (summary_row, ["Average_Coverage_Ratio", "average_coverage_ratio"]),
        ],
        0.0,
    )
    run_status = _first_text([(run_row, ["Run_Status", "run_status"])], "UNKNOWN")
    adequacy_class = _first_text(
        [(adequacy_row, ["Sample_Adequacy_Class", "sample_adequacy_class"])],
        "PARTIAL_SAMPLE_UNAVAILABLE",
    )
    comparison_class = _first_text(
        [(comparison_row, ["Partial_Comparison_Class", "partial_comparison_class"])],
        "PARTIAL_COMPARISON_UNAVAILABLE",
    )
    condition_count = _first_int(
        [
            (run_row, ["Condition_Profile_Count", "condition_profile_count"]),
            (adequacy_row, ["Condition_Profile_Count", "condition_profile_count"]),
        ],
        0,
    )
    status = classify_partial_sample_status(run_status, adequacy_class)
    return [
        PartialSampleReviewRow(
            candidate_id=candidate_id,
            sample_label=sample_label,
            coverage_ratio=round(coverage_ratio, 4),
            run_status=run_status,
            sample_adequacy_class=adequacy_class,
            partial_comparison_class=comparison_class,
            condition_profile_count=condition_count,
            partial_sample_status=status,
            partial_sample_diagnostic=_status_diagnostic(status),
        )
    ]


def load_partial_structure_state_snapshot(
    config: H4PartialComplementaryDispersionReviewConfig,
) -> PartialStructureStateSnapshot | None:
    frame = read_optional_csv(config.partial_validation_dir / "h4_partial_structure_state_summary.csv")
    row = _candidate_or_first(frame, config.candidate_id)
    if row is None:
        return None
    return PartialStructureStateSnapshot(
        candidate_id=text_value(row, ["Candidate_ID", "candidate_id"], config.candidate_id),
        sample_label=text_value(row, ["Sample_Label", "sample_label"], config.partial_sample_label),
        partial_state_profile=text_value(row, ["State_Diversity_Profile", "state_diversity_profile"], "NO_STATE_DATA"),
        partial_unique_state_count=int_value(row, ["Unique_State_Count", "unique_state_count"], 0),
        partial_most_common_state=text_value(row, ["Most_Common_State", "most_common_state"], "NO_STATE_DATA"),
    )


def load_partial_transition_snapshot(
    config: H4PartialComplementaryDispersionReviewConfig,
) -> PartialTransitionSnapshot | None:
    frame = read_optional_csv(config.partial_validation_dir / "h4_partial_transition_summary.csv")
    row = _candidate_or_first(frame, config.candidate_id)
    if row is None:
        return None
    return PartialTransitionSnapshot(
        candidate_id=text_value(row, ["Candidate_ID", "candidate_id"], config.candidate_id),
        sample_label=text_value(row, ["Sample_Label", "sample_label"], config.partial_sample_label),
        partial_most_common_transition=text_value(
            row,
            ["Most_Common_Transition", "most_common_transition"],
            "NO_TRANSITION_DATA",
        ),
        partial_unique_transition_count=int_value(row, ["Unique_Transition_Count", "unique_transition_count"], 0),
    )


def classify_partial_sample_status(run_status: str, sample_adequacy_class: str) -> str:
    run = run_status.strip().upper()
    adequacy = sample_adequacy_class.strip().upper()
    if run == "COMPLETED" and adequacy == "PARTIAL_SAMPLE_RESEARCH_USABLE":
        return "PARTIAL_VALIDATED"
    if run == "COMPLETED" and adequacy == "PARTIAL_SAMPLE_LIMITED":
        return "PARTIAL_LIMITED"
    if run in {"FAILED", "SKIPPED"} or adequacy == "PARTIAL_SAMPLE_UNAVAILABLE":
        return "PARTIAL_UNAVAILABLE"
    return "PARTIAL_UNKNOWN"


def _row_for_candidate(frame, candidate_id: str):
    if frame.empty:
        return None
    for _, row in frame.iterrows():
        if text_value(row, ["Candidate_ID", "candidate_id"]) == candidate_id:
            return row
    return None


def _candidate_or_first(frame, candidate_id: str):
    row = _row_for_candidate(frame, candidate_id)
    if row is not None:
        return row
    return first_row(frame)


def _first_text(row_specs: list[tuple[object | None, list[str]]], default: str) -> str:
    for row, aliases in row_specs:
        if row is None:
            continue
        raw = text_value(row, aliases, "")
        if raw:
            return raw
    return default


def _first_number(row_specs: list[tuple[object | None, list[str]]], default: float) -> float:
    for row, aliases in row_specs:
        if row is None:
            continue
        raw = number_value(row, aliases, default)
        if raw != default:
            return raw
    return default


def _first_int(row_specs: list[tuple[object | None, list[str]]], default: int) -> int:
    for row, aliases in row_specs:
        if row is None:
            continue
        raw = int_value(row, aliases, default)
        if raw != default:
            return raw
    return default


def _status_diagnostic(status: str) -> str:
    diagnostics = {
        "PARTIAL_VALIDATED": "Partial sample is usable for complementary review.",
        "PARTIAL_LIMITED": "Partial sample is available with limited interpretation.",
        "PARTIAL_UNAVAILABLE": "Partial sample is unavailable for complementary review.",
    }
    return diagnostics.get(status, "Partial sample status could not be fully resolved.")
