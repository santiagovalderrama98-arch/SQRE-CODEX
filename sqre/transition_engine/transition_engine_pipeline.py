"""SQRE Transition Engine pipeline."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from sqre.transition_engine.config import TransitionEngineConfig
from sqre.transition_engine.loader import load_market_states
from sqre.transition_engine.matrix import build_transition_matrix
from sqre.transition_engine.models import (
    MarketStateInput,
    StateTransition,
    TransitionEngineSummary,
    TransitionMatrixRow,
    TransitionSequence,
)
from sqre.transition_engine.reports import write_transition_engine_report
from sqre.transition_engine.sequences import build_transition_sequences
from sqre.transition_engine.transitions import build_state_transitions


def run_transition_engine(
    states_path: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: TransitionEngineConfig | None = None,
) -> TransitionEngineSummary:
    active_config = config or TransitionEngineConfig()
    output_directory = Path(output_dir)
    report = Path(report_path)
    output_directory.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    states = load_market_states(states_path)
    transitions = build_state_transitions(states, active_config)
    matrix_rows = build_transition_matrix(transitions)
    sequences = build_transition_sequences(states, transitions, active_config)

    state_transitions_path = output_directory / "state_transitions.csv"
    transition_matrix_path = output_directory / "transition_matrix.csv"
    transition_sequences_path = output_directory / "transition_sequences.csv"

    _state_transitions_frame(transitions).to_csv(state_transitions_path, index=False)
    _transition_matrix_frame(matrix_rows).to_csv(transition_matrix_path, index=False)
    _transition_sequences_frame(sequences).to_csv(transition_sequences_path, index=False)

    summary = _build_summary(
        states=states,
        transitions=transitions,
        matrix_rows=matrix_rows,
        sequences=sequences,
        state_transitions_path=state_transitions_path,
        transition_matrix_path=transition_matrix_path,
        transition_sequences_path=transition_sequences_path,
        report_path=report,
    )
    write_transition_engine_report(report, summary, transitions, matrix_rows, sequences)
    return summary


def _state_transitions_frame(transitions: list[StateTransition]) -> pd.DataFrame:
    columns = [
        "Transition_ID",
        "From_State_ID",
        "To_State_ID",
        "From_Structure_ID",
        "To_Structure_ID",
        "Symbol",
        "Timeframe",
        "From_Market_State",
        "To_Market_State",
        "Transition_Label",
        "Start_Time",
        "End_Time",
        "Transition_Duration_Seconds",
        "From_Direction",
        "To_Direction",
        "State_Changed",
        "Direction_Changed",
        "Primary_Transition_Type",
        "Transition_Tags",
        "Persistence_Change",
        "Complexity_Change",
        "Stability_Change",
        "Efficiency_Change",
        "Density_Change",
        "Volatility_Change",
        "Symmetry_Change",
        "Structural_Confidence_Change",
        "State_Confidence_Change",
        "Price_Displacement_Change",
        "Duration_Change",
        "Event_Count_Change",
        "Leg_Count_Change",
        "Transition_Magnitude",
        "Transition_Stability",
        "Structural_Quality_Change",
    ]
    rows = []
    for transition in transitions:
        metrics = transition.metrics
        rows.append(
            {
                "Transition_ID": transition.transition_id,
                "From_State_ID": transition.from_state_id,
                "To_State_ID": transition.to_state_id,
                "From_Structure_ID": transition.from_structure_id,
                "To_Structure_ID": transition.to_structure_id,
                "Symbol": transition.symbol,
                "Timeframe": transition.timeframe,
                "From_Market_State": transition.from_market_state,
                "To_Market_State": transition.to_market_state,
                "Transition_Label": transition.transition_label,
                "Start_Time": transition.start_time,
                "End_Time": transition.end_time,
                "Transition_Duration_Seconds": transition.transition_duration_seconds,
                "From_Direction": transition.from_direction,
                "To_Direction": transition.to_direction,
                "State_Changed": transition.state_changed,
                "Direction_Changed": transition.direction_changed,
                "Primary_Transition_Type": transition.primary_transition_type,
                "Transition_Tags": transition.transition_tags,
                "Persistence_Change": metrics.persistence_change,
                "Complexity_Change": metrics.complexity_change,
                "Stability_Change": metrics.stability_change,
                "Efficiency_Change": metrics.efficiency_change,
                "Density_Change": metrics.density_change,
                "Volatility_Change": metrics.volatility_change,
                "Symmetry_Change": metrics.symmetry_change,
                "Structural_Confidence_Change": metrics.structural_confidence_change,
                "State_Confidence_Change": metrics.state_confidence_change,
                "Price_Displacement_Change": metrics.price_displacement_change,
                "Duration_Change": metrics.duration_change,
                "Event_Count_Change": metrics.event_count_change,
                "Leg_Count_Change": metrics.leg_count_change,
                "Transition_Magnitude": metrics.transition_magnitude,
                "Transition_Stability": metrics.transition_stability,
                "Structural_Quality_Change": metrics.structural_quality_change,
            }
        )
    return pd.DataFrame(rows, columns=columns)


def _transition_matrix_frame(rows: list[TransitionMatrixRow]) -> pd.DataFrame:
    columns = [
        "From_State",
        "To_State",
        "Count",
        "Probability",
        "Percentage",
        "Average_Transition_Magnitude",
        "Average_Transition_Stability",
        "Average_State_Confidence_Change",
        "Average_Structural_Quality_Change",
    ]
    return pd.DataFrame(
        [
            {
                "From_State": row.from_state,
                "To_State": row.to_state,
                "Count": row.count,
                "Probability": row.probability,
                "Percentage": row.percentage,
                "Average_Transition_Magnitude": row.average_transition_magnitude,
                "Average_Transition_Stability": row.average_transition_stability,
                "Average_State_Confidence_Change": row.average_state_confidence_change,
                "Average_Structural_Quality_Change": row.average_structural_quality_change,
            }
            for row in rows
        ],
        columns=columns,
    )


def _transition_sequences_frame(sequences: list[TransitionSequence]) -> pd.DataFrame:
    columns = [
        "Sequence_ID",
        "Sequence",
        "Length",
        "Count",
        "Frequency",
        "Percentage",
        "Average_Duration",
        "Average_Transition_Magnitude",
    ]
    return pd.DataFrame(
        [
            {
                "Sequence_ID": sequence.sequence_id,
                "Sequence": sequence.sequence,
                "Length": sequence.length,
                "Count": sequence.count,
                "Frequency": sequence.frequency,
                "Percentage": sequence.percentage,
                "Average_Duration": sequence.average_duration,
                "Average_Transition_Magnitude": sequence.average_transition_magnitude,
            }
            for sequence in sequences
        ],
        columns=columns,
    )


def _build_summary(
    *,
    states: list[MarketStateInput],
    transitions: list[StateTransition],
    matrix_rows: list[TransitionMatrixRow],
    sequences: list[TransitionSequence],
    state_transitions_path: Path,
    transition_matrix_path: Path,
    transition_sequences_path: Path,
    report_path: Path,
) -> TransitionEngineSummary:
    transition_count = len(transitions)
    return TransitionEngineSummary(
        symbol=_summary_value([state.symbol for state in states]),
        timeframe=_summary_value([state.timeframe for state in states]),
        period_start=min((state.start_time for state in states), default=None),
        period_end=max((state.end_time for state in states), default=None),
        states_processed=len(states),
        transitions_generated=transition_count,
        unique_states=len({state.market_state for state in states}),
        unique_transitions=len({transition.transition_label for transition in transitions}),
        most_common_transition=_most_common_transition(transitions),
        most_common_sequence=sequences[0].sequence if sequences else "NONE",
        state_change_rate=_rate(sum(transition.state_changed for transition in transitions), transition_count),
        direction_change_rate=_rate(sum(transition.direction_changed for transition in transitions), transition_count),
        average_transition_duration=_average(
            transition.transition_duration_seconds for transition in transitions
        ),
        average_transition_magnitude=_average(
            transition.metrics.transition_magnitude for transition in transitions
        ),
        average_transition_stability=_average(
            transition.metrics.transition_stability for transition in transitions
        ),
        average_state_confidence_change=_average(
            transition.metrics.state_confidence_change for transition in transitions
        ),
        average_structural_quality_change=_average(
            transition.metrics.structural_quality_change for transition in transitions
        ),
        state_transitions_path=state_transitions_path,
        transition_matrix_path=transition_matrix_path,
        transition_sequences_path=transition_sequences_path,
        report_path=report_path,
    )


def _summary_value(values: list[str]) -> str:
    unique_values = sorted(set(values))
    if not unique_values:
        return "UNKNOWN"
    if len(unique_values) == 1:
        return unique_values[0]
    return "MULTIPLE"


def _most_common_transition(transitions: list[StateTransition]) -> str:
    if not transitions:
        return "NONE"
    counts = Counter(transition.transition_label for transition in transitions)
    return max(counts, key=lambda label: (counts[label], label))


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return count / total


def _average(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
