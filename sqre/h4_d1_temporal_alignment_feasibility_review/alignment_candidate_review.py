"""Alignment candidate review for H4/D1 temporal feasibility."""

from __future__ import annotations

from sqre.h4_d1_temporal_alignment_feasibility_review.models import (
    AlignmentCandidateReviewRow,
    TemporalKeyInventoryRow,
)
from sqre.h4_d1_temporal_alignment_feasibility_review.temporal_key_inventory import (
    has_condition_only,
    has_exact_timestamp,
    has_scenario_period,
    has_start_end,
    has_temporal_alignment_keys,
)


def build_alignment_candidate_review(keys: list[TemporalKeyInventoryRow]) -> list[AlignmentCandidateReviewRow]:
    h4_sources = [row for row in keys if _is_h4_source(row)]
    d1_sources = [row for row in keys if _is_d1_source(row)]
    rows: list[AlignmentCandidateReviewRow] = []
    for h4 in h4_sources:
        for d1 in d1_sources:
            rows.append(_candidate_row(len(rows) + 1, h4, d1))
    return rows


def _candidate_row(index: int, h4: TemporalKeyInventoryRow, d1: TemporalKeyInventoryRow) -> AlignmentCandidateReviewRow:
    method, feasibility, confidence, diagnostic = classify_candidate(h4, d1)
    return AlignmentCandidateReviewRow(
        candidate_id=f"CAND_{index:06d}",
        h4_source_name=h4.source_name,
        d1_source_name=d1.source_name,
        h4_key_status=h4.temporal_key_status,
        d1_key_status=d1.temporal_key_status,
        potential_alignment_method=method,
        alignment_feasibility_class=feasibility,
        alignment_confidence_class=confidence,
        candidate_diagnostic=diagnostic,
    )


def classify_candidate(
    h4: TemporalKeyInventoryRow,
    d1: TemporalKeyInventoryRow,
) -> tuple[str, str, str, str]:
    if h4.temporal_key_status == "INPUT_MISSING" or d1.temporal_key_status == "INPUT_MISSING":
        return (
            "NO_ALIGNMENT_METHOD_AVAILABLE",
            "INPUT_LIMITED",
            "NO_TEMPORAL_ALIGNMENT_CONFIDENCE",
            "One or both source files are missing.",
        )
    if has_exact_timestamp(h4) and has_exact_timestamp(d1):
        return (
            "EXACT_TIMESTAMP_JOIN",
            "READY_FOR_EXACT_TIMESTAMP_ALIGNMENT",
            "HIGH_CONFIDENCE_TEMPORAL_ALIGNMENT_READY",
            "Both H4 and D1 sources expose exact timestamp columns.",
        )
    if has_scenario_period(h4) and has_scenario_period(d1):
        return (
            "SCENARIO_PERIOD_JOIN",
            "READY_FOR_SCENARIO_PERIOD_ALIGNMENT",
            "MODERATE_CONFIDENCE_TEMPORAL_ALIGNMENT_READY",
            "Both sides expose scenario-period keys.",
        )
    if has_start_end(h4) and (has_exact_timestamp(d1) or has_start_end(d1)):
        return (
            "H4_INTERVAL_TO_D1_INTERVAL_OVERLAP",
            "READY_FOR_INTERVAL_OVERLAP_ALIGNMENT",
            "MODERATE_CONFIDENCE_TEMPORAL_ALIGNMENT_READY",
            "H4 interval keys can be reviewed against D1 timestamp or interval keys.",
        )
    if has_start_end(h4) and has_start_end(d1):
        return (
            "DATE_RANGE_OVERLAP",
            "READY_FOR_INTERVAL_OVERLAP_ALIGNMENT",
            "LOW_CONFIDENCE_TEMPORAL_ALIGNMENT_READY",
            "Both sides expose date ranges that can be reviewed for overlap.",
        )
    if has_condition_only(h4) and has_condition_only(d1):
        return (
            "CONDITION_ONLY_MATCH_NOT_TEMPORAL",
            "CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT",
            "NO_TEMPORAL_ALIGNMENT_CONFIDENCE",
            "Condition label/window keys can match profiles, but they do not prove same-time alignment.",
        )
    h4_ready = has_temporal_alignment_keys(h4)
    d1_ready = has_temporal_alignment_keys(d1)
    if d1_ready and not h4_ready:
        return (
            "NO_ALIGNMENT_METHOD_AVAILABLE",
            "NOT_READY_MISSING_H4_TEMPORAL_KEYS",
            "NO_TEMPORAL_ALIGNMENT_CONFIDENCE",
            "D1 has temporal keys, but H4 context lacks timestamp, interval, or scenario-period keys.",
        )
    if h4_ready and not d1_ready:
        return (
            "NO_ALIGNMENT_METHOD_AVAILABLE",
            "NOT_READY_MISSING_D1_TEMPORAL_KEYS",
            "NO_TEMPORAL_ALIGNMENT_CONFIDENCE",
            "H4 has temporal keys, but D1 context lacks timestamp, interval, or scenario-period keys.",
        )
    return (
        "NO_ALIGNMENT_METHOD_AVAILABLE",
        "NOT_READY_MISSING_BOTH_TEMPORAL_KEYS",
        "NO_TEMPORAL_ALIGNMENT_CONFIDENCE",
        "Both H4 and D1 sources lack usable same-time temporal alignment keys.",
    )


def _is_h4_source(row: TemporalKeyInventoryRow) -> bool:
    return row.source_type == "H4_COMBINED_CONTEXT"


def _is_d1_source(row: TemporalKeyInventoryRow) -> bool:
    return row.source_type.startswith("D1")
