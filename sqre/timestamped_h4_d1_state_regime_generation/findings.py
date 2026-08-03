"""Findings for timestamped H4/D1 state/regime generation."""

from __future__ import annotations

from sqre.timestamped_h4_d1_state_regime_generation.models import CoverageReviewRow, TimestampedH4D1StateRegimeSummary


def build_summary(coverage: CoverageReviewRow) -> TimestampedH4D1StateRegimeSummary:
    dominant = _dominant_class(coverage)
    readiness = _readiness_flag(coverage)
    return TimestampedH4D1StateRegimeSummary(
        symbol=coverage.symbol,
        h4_timeframe=coverage.h4_timeframe,
        d1_timeframe=coverage.d1_timeframe,
        h4_input_row_count=coverage.h4_input_row_count,
        d1_input_row_count=coverage.d1_input_row_count,
        h4_state_row_count=coverage.h4_state_row_count,
        h4_transition_row_count=coverage.h4_transition_row_count,
        d1_state_row_count=coverage.d1_state_row_count,
        dominant_generation_coverage_class=dominant,
        timestamped_h4_d1_state_regime_readiness_flag=readiness,
        timestamped_h4_d1_state_regime_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_follow_up(readiness),
    )


def readiness_lines(summary: TimestampedH4D1StateRegimeSummary | None) -> list[str]:
    if summary is None:
        return ["- Timestamped H4/D1 summary was not produced."]
    return [
        f"- Dominant generation coverage class: {summary.dominant_generation_coverage_class}",
        f"- Timestamped H4/D1 readiness flag: {summary.timestamped_h4_d1_state_regime_readiness_flag}",
        f"- Recommended follow-up: {summary.recommended_follow_up}",
        "- Generated timestamps are future alignment keys only.",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4/D1 same-time alignment table",
        "D1 regime context review using synchronized data",
        "H4/D1 same-time contextual transition review",
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
        "No H4/D1 same-time alignment was produced.",
        "No H4/D1 same-time interpretation was produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on synchronized local input files.",
        "Data sample is partial if H4 source was limited by provider row limits.",
        "State/regime generation depends on existing SQRE structural modules.",
        "Generated outputs are research artifacts only.",
        "No operational decision is produced.",
    ]


def _dominant_class(coverage: CoverageReviewRow) -> str:
    classes = [
        coverage.h4_state_coverage_class,
        coverage.h4_transition_coverage_class,
        coverage.d1_state_coverage_class,
    ]
    priority = [
        "INPUT_MISSING",
        "TIMESTAMPED_OUTPUT_MISSING",
        "PARTIAL_TIMESTAMPED_OUTPUT_AVAILABLE",
        "TIMESTAMPED_OUTPUT_AVAILABLE",
    ]
    return min(classes, key=priority.index)


def _readiness_flag(coverage: CoverageReviewRow) -> str:
    classes = {
        coverage.h4_state_coverage_class,
        coverage.h4_transition_coverage_class,
        coverage.d1_state_coverage_class,
    }
    if "INPUT_MISSING" in classes:
        return "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    if classes == {"TIMESTAMPED_OUTPUT_AVAILABLE"}:
        return "READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE"
    if coverage.h4_state_coverage_class == "TIMESTAMPED_OUTPUT_MISSING":
        return "NOT_READY_H4_STATE_OUTPUT_MISSING"
    if coverage.h4_transition_coverage_class == "TIMESTAMPED_OUTPUT_MISSING":
        return "NOT_READY_H4_TRANSITION_OUTPUT_MISSING"
    if coverage.d1_state_coverage_class == "TIMESTAMPED_OUTPUT_MISSING":
        return "NOT_READY_D1_STATE_OUTPUT_MISSING"
    if "TIMESTAMPED_OUTPUT_MISSING" in classes:
        return "NOT_READY_TIMESTAMPED_STATE_REGIME_OUTPUTS_MISSING"
    return "PARTIAL_READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE"


def _diagnostic(readiness: str) -> str:
    mapping = {
        "READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE": "Timestamped H4/D1 state/regime outputs are ready for later same-time alignment table construction.",
        "PARTIAL_READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE": "Timestamped H4/D1 state/regime outputs are partially available and need review.",
        "NOT_READY_H4_STATE_OUTPUT_MISSING": "Timestamped H4 market state output is missing.",
        "NOT_READY_H4_TRANSITION_OUTPUT_MISSING": "Timestamped H4 state transition output is missing.",
        "NOT_READY_D1_STATE_OUTPUT_MISSING": "Timestamped D1 market state/regime output is missing.",
        "NOT_READY_TIMESTAMPED_STATE_REGIME_OUTPUTS_MISSING": "Timestamped state/regime outputs are missing.",
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "Synchronized input completeness requires review.",
    }
    return mapping.get(readiness, "Timestamped generation readiness could not be classified.")


def _follow_up(readiness: str) -> str:
    if readiness in {
        "READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE",
        "PARTIAL_READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE",
    }:
        return "BUILD_H4_D1_SAME_TIME_ALIGNMENT_TABLE"
    if readiness == "INPUT_COMPLETENESS_REVIEW_REQUIRED":
        return "REVIEW_SYNCHRONIZED_INPUT_COMPLETENESS"
    return "REVIEW_TIMEFRAME_PIPELINE_ADAPTER"
