"""Transition Engine report writer."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from sqre.transition_engine.models import (
    StateTransition,
    TransitionEngineSummary,
    TransitionMatrixRow,
    TransitionSequence,
)


PRIMARY_TYPE_LABELS = {
    "SAME_STATE": "Same State",
    "STATE_CHANGE": "State Change",
    "DIRECTION_CHANGE": "Direction Change",
}

TAG_LABELS = {
    "CONFIDENCE_EXPANSION": "Confidence Expansion",
    "CONFIDENCE_DETERIORATION": "Confidence Deterioration",
    "CONFIDENCE_STABLE": "Confidence Stable",
    "STRUCTURAL_IMPROVEMENT": "Structural Improvement",
    "STRUCTURAL_DETERIORATION": "Structural Deterioration",
    "STRUCTURAL_STABLE": "Structural Stable",
    "HIGH_MAGNITUDE": "High Magnitude",
    "MODERATE_MAGNITUDE": "Moderate Magnitude",
    "LOW_MAGNITUDE": "Low Magnitude",
}


def write_transition_engine_report(
    path: Path | str,
    summary: TransitionEngineSummary,
    transitions: list[StateTransition],
    matrix_rows: list[TransitionMatrixRow],
    sequences: list[TransitionSequence],
) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _build_report(summary, transitions, matrix_rows, sequences),
        encoding="utf-8",
    )


def _build_report(
    summary: TransitionEngineSummary,
    transitions: list[StateTransition],
    matrix_rows: list[TransitionMatrixRow],
    sequences: list[TransitionSequence],
) -> str:
    transition_type_counts = Counter(transition.primary_transition_type for transition in transitions)
    tag_counts = Counter(tag for transition in transitions for tag in transition.transition_tags.split("|") if tag)

    lines = [
        "SQRE Transition Engine Report",
        "=============================",
        "",
        f"Symbol: {summary.symbol}",
        f"Timeframe: {summary.timeframe}",
        f"Period: {_period(summary)}",
        f"States Processed: {summary.states_processed}",
        f"Transitions Generated: {summary.transitions_generated}",
        f"Unique States: {summary.unique_states}",
        f"Unique Transitions: {summary.unique_transitions}",
        "",
        f"Most Common Transition: {summary.most_common_transition}",
        f"Most Common Sequence: {summary.most_common_sequence}",
        f"State Change Rate: {summary.state_change_rate:.4f}",
        f"Direction Change Rate: {summary.direction_change_rate:.4f}",
        f"Average Transition Duration: {summary.average_transition_duration:.2f}",
        f"Average Transition Magnitude: {summary.average_transition_magnitude:.4f}",
        f"Average Transition Stability: {summary.average_transition_stability:.4f}",
        f"Average State Confidence Change: {summary.average_state_confidence_change:.4f}",
        f"Average Structural Quality Change: {summary.average_structural_quality_change:.4f}",
        "",
        "Transitions by Type:",
    ]
    lines.extend(
        f"- {label}: {transition_type_counts.get(key, 0)}"
        for key, label in PRIMARY_TYPE_LABELS.items()
    )
    lines.append("")
    lines.append("Transition Tags:")
    lines.extend(f"- {label}: {tag_counts.get(key, 0)}" for key, label in TAG_LABELS.items())
    lines.extend(
        [
            "",
            "Key Observations:",
            "- This report is descriptive and summarizes observed state transitions.",
            "- Transition frequencies are calculated only from the processed dataset.",
            "- No trading signals or operational recommendations are generated.",
            "",
        ]
    )
    return "\n".join(lines)


def _period(summary: TransitionEngineSummary) -> str:
    if summary.period_start is None or summary.period_end is None:
        return "UNKNOWN"
    return f"{summary.period_start} -> {summary.period_end}"
