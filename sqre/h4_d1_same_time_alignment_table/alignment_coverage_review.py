"""Coverage review for H4/D1 same-time alignment."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_same_time_alignment_table.config import H4D1SameTimeAlignmentConfig
from sqre.h4_d1_same_time_alignment_table.models import AlignmentCoverageReviewRow


def build_alignment_coverage_review(
    transition_alignment: pd.DataFrame,
    state_alignment: pd.DataFrame,
    d1_states: pd.DataFrame,
    config: H4D1SameTimeAlignmentConfig,
) -> AlignmentCoverageReviewRow:
    transition_count = len(transition_alignment)
    state_count = len(state_alignment)
    aligned_transition_count = _aligned_count(transition_alignment)
    aligned_state_count = _aligned_count(state_alignment)
    transition_ratio = _ratio(aligned_transition_count, transition_count)
    state_ratio = _ratio(aligned_state_count, state_count)
    transition_class = _coverage_class(
        transition_count,
        len(d1_states),
        transition_ratio,
        config.minimum_transition_alignment_ratio,
    )
    state_class = _coverage_class(state_count, len(d1_states), state_ratio, config.minimum_state_alignment_ratio)
    overall = _dominant_class([transition_class, state_class])
    return AlignmentCoverageReviewRow(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        h4_transition_row_count=transition_count,
        aligned_h4_transition_row_count=aligned_transition_count,
        unaligned_h4_transition_row_count=transition_count - aligned_transition_count,
        h4_state_row_count=state_count,
        aligned_h4_state_row_count=aligned_state_count,
        unaligned_h4_state_row_count=state_count - aligned_state_count,
        d1_state_row_count=len(d1_states),
        transition_alignment_ratio=round(transition_ratio, 6),
        state_alignment_ratio=round(state_ratio, 6),
        transition_alignment_coverage_class=transition_class,
        state_alignment_coverage_class=state_class,
        overall_alignment_coverage_class=overall,
        coverage_diagnostic=_diagnostic(overall),
    )


def _aligned_count(frame: pd.DataFrame) -> int:
    if frame.empty or "Alignment_Method" not in frame.columns:
        return 0
    return int((frame["Alignment_Method"] != "NO_D1_SAME_TIME_MATCH").sum())


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _coverage_class(input_count: int, d1_count: int, ratio: float, minimum_ratio: float) -> str:
    if input_count == 0 or d1_count == 0:
        return "INPUT_MISSING"
    if ratio == 1:
        return "FULL_SAME_TIME_ALIGNMENT_COVERAGE"
    if ratio >= minimum_ratio:
        return "ACCEPTABLE_SAME_TIME_ALIGNMENT_COVERAGE"
    if ratio >= 0.50:
        return "PARTIAL_SAME_TIME_ALIGNMENT_COVERAGE"
    if ratio > 0:
        return "LOW_SAME_TIME_ALIGNMENT_COVERAGE"
    return "NO_SAME_TIME_ALIGNMENT_COVERAGE"


def _dominant_class(classes: list[str]) -> str:
    priority = [
        "INPUT_MISSING",
        "NO_SAME_TIME_ALIGNMENT_COVERAGE",
        "LOW_SAME_TIME_ALIGNMENT_COVERAGE",
        "PARTIAL_SAME_TIME_ALIGNMENT_COVERAGE",
        "ACCEPTABLE_SAME_TIME_ALIGNMENT_COVERAGE",
        "FULL_SAME_TIME_ALIGNMENT_COVERAGE",
    ]
    return min(classes, key=priority.index)


def _diagnostic(coverage_class: str) -> str:
    mapping = {
        "FULL_SAME_TIME_ALIGNMENT_COVERAGE": "All H4 timestamped rows have same-time D1 context.",
        "ACCEPTABLE_SAME_TIME_ALIGNMENT_COVERAGE": "Same-time D1 context coverage meets configured research minimums.",
        "PARTIAL_SAME_TIME_ALIGNMENT_COVERAGE": "Same-time D1 context coverage is partial and should be reviewed.",
        "LOW_SAME_TIME_ALIGNMENT_COVERAGE": "Same-time D1 context coverage is low.",
        "NO_SAME_TIME_ALIGNMENT_COVERAGE": "No H4 timestamped rows matched D1 same-time context.",
        "INPUT_MISSING": "Required timestamped H4 or D1 inputs are missing or empty.",
    }
    return mapping.get(coverage_class, "Same-time alignment coverage could not be classified.")
