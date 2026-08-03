"""Findings for H4/D1 same-time alignment."""

from __future__ import annotations

from sqre.h4_d1_same_time_alignment_table.models import AlignmentCoverageReviewRow, H4D1SameTimeAlignmentSummary


def build_summary(coverage: AlignmentCoverageReviewRow) -> H4D1SameTimeAlignmentSummary:
    readiness = _readiness_flag(coverage)
    return H4D1SameTimeAlignmentSummary(
        symbol=coverage.symbol,
        h4_timeframe=coverage.h4_timeframe,
        d1_timeframe=coverage.d1_timeframe,
        h4_transition_row_count=coverage.h4_transition_row_count,
        aligned_h4_transition_row_count=coverage.aligned_h4_transition_row_count,
        unaligned_h4_transition_row_count=coverage.unaligned_h4_transition_row_count,
        h4_state_row_count=coverage.h4_state_row_count,
        aligned_h4_state_row_count=coverage.aligned_h4_state_row_count,
        unaligned_h4_state_row_count=coverage.unaligned_h4_state_row_count,
        d1_state_row_count=coverage.d1_state_row_count,
        transition_alignment_ratio=coverage.transition_alignment_ratio,
        state_alignment_ratio=coverage.state_alignment_ratio,
        dominant_alignment_coverage_class=coverage.overall_alignment_coverage_class,
        h4_d1_same_time_alignment_readiness_flag=readiness,
        h4_d1_same_time_alignment_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_follow_up(readiness),
    )


def readiness_lines(summary: H4D1SameTimeAlignmentSummary | None) -> list[str]:
    if summary is None:
        return ["- H4/D1 same-time alignment summary was not produced."]
    return [
        f"- Dominant alignment coverage class: {summary.dominant_alignment_coverage_class}",
        f"- H4/D1 same-time alignment readiness flag: {summary.h4_d1_same_time_alignment_readiness_flag}",
        f"- Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4/D1 same-time contextual transition review",
        "H4/D1 aligned context outcome research",
        "D1 regime context adequacy review",
        "Provider history coverage review",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No provider behavior was changed.",
        "No H4/D1 same-time interpretation was produced.",
        "No outcome research was produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local timestamped H4/D1 state/regime outputs.",
        "The H4 source sample may be partial due to provider row limits.",
        "Same-time alignment quality depends on D1 state coverage.",
        "Data-level alignment is not equivalent to contextual interpretation.",
        "No operational decision is produced.",
    ]


def _readiness_flag(coverage: AlignmentCoverageReviewRow) -> str:
    if coverage.overall_alignment_coverage_class == "INPUT_MISSING":
        return "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    if coverage.overall_alignment_coverage_class == "FULL_SAME_TIME_ALIGNMENT_COVERAGE":
        return "READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW"
    if coverage.overall_alignment_coverage_class == "ACCEPTABLE_SAME_TIME_ALIGNMENT_COVERAGE":
        return "PARTIAL_READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW"
    if coverage.d1_state_row_count == 0:
        return "NOT_READY_D1_CONTEXT_COVERAGE_INSUFFICIENT"
    if coverage.transition_alignment_ratio == 0 and coverage.state_alignment_ratio == 0:
        return "NOT_READY_SAME_TIME_ALIGNMENT_MISSING"
    return "NOT_READY_H4_TIMESTAMP_COVERAGE_INSUFFICIENT"


def _diagnostic(readiness: str) -> str:
    mapping = {
        "READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW": "H4/D1 same-time alignment tables are ready for a later contextual review.",
        "PARTIAL_READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW": "H4/D1 same-time alignment coverage is acceptable but not complete.",
        "NOT_READY_D1_CONTEXT_COVERAGE_INSUFFICIENT": "D1 same-time context coverage is insufficient.",
        "NOT_READY_H4_TIMESTAMP_COVERAGE_INSUFFICIENT": "H4 timestamp coverage requires review before later contextual work.",
        "NOT_READY_SAME_TIME_ALIGNMENT_MISSING": "No H4 rows matched D1 same-time context.",
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "Required timestamped H4/D1 inputs require completeness review.",
    }
    return mapping.get(readiness, "H4/D1 same-time alignment readiness could not be classified.")


def _follow_up(readiness: str) -> str:
    if readiness in {
        "READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW",
        "PARTIAL_READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW",
    }:
        return "H4_D1_SAME_TIME_CONTEXTUAL_TRANSITION_REVIEW"
    if readiness == "NOT_READY_D1_CONTEXT_COVERAGE_INSUFFICIENT":
        return "REVIEW_D1_TIMESTAMPED_STATE_COVERAGE"
    if readiness == "INPUT_COMPLETENESS_REVIEW_REQUIRED":
        return "REVIEW_TIMESTAMPED_STATE_REGIME_INPUT_COMPLETENESS"
    return "REVIEW_H4_D1_SAME_TIME_ALIGNMENT_COVERAGE"
