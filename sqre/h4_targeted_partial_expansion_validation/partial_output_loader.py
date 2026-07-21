"""Load generated partial validation outputs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.loader import (
    count_false_like,
    mean_column,
    read_optional_csv,
    resolve_column,
)
from sqre.h4_targeted_partial_expansion_validation.models import (
    PartialCandidate,
    PartialPriceOutcomeSummary,
    PartialStructureStateSummary,
    PartialTransitionSummary,
    PartialValidationRunSummary,
)


def load_structure_state_summary(
    candidate: PartialCandidate,
    run: PartialValidationRunSummary,
    config: H4TargetedPartialExpansionValidationConfig,
) -> PartialStructureStateSummary:
    processed_dir = config.output_dir / candidate.candidate_id / "processed"
    structures = read_optional_csv(processed_dir / "structures.csv")
    states = read_optional_csv(processed_dir / "market_states.csv")
    average_duration = mean_column(structures, ["Duration_Seconds", "duration_seconds"])
    average_range = abs(mean_column(structures, ["Price_Displacement", "price_displacement"])) / config.pip_size
    state_column = resolve_column(states, ["Market_State", "market_state"])
    unique_state_count = int(states[state_column].nunique()) if state_column and not states.empty else 0
    most_common_state = _most_common(states[state_column]) if state_column and not states.empty else "NO_STATE_DATA"
    diversity = _state_diversity(unique_state_count)
    diagnostic = "Partial sample generated structure and state context." if run.run_status == "COMPLETED" else run.run_diagnostic
    return PartialStructureStateSummary(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        ohlc_rows=run.ohlc_rows,
        structure_count=len(structures),
        average_structure_duration=round(average_duration, 4),
        average_structure_range_pips=round(average_range, 4),
        unique_state_count=unique_state_count,
        most_common_state=most_common_state,
        state_diversity_profile=diversity,
        structure_state_diagnostic=diagnostic,
    )


def load_transition_summary(
    candidate: PartialCandidate,
    run: PartialValidationRunSummary,
    config: H4TargetedPartialExpansionValidationConfig,
) -> PartialTransitionSummary:
    transitions = read_optional_csv(config.output_dir / candidate.candidate_id / "processed" / "state_transitions.csv")
    label_column = resolve_column(transitions, ["Transition_Label", "transition_label"])
    from_column = resolve_column(transitions, ["From_Market_State", "from_market_state"])
    to_column = resolve_column(transitions, ["To_Market_State", "to_market_state"])
    labels = transitions[label_column] if label_column and not transitions.empty else pd.Series(dtype=str)
    from_states = transitions[from_column] if from_column and not transitions.empty else pd.Series(dtype=str)
    to_states = transitions[to_column] if to_column and not transitions.empty else pd.Series(dtype=str)
    return PartialTransitionSummary(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        transition_count=len(transitions),
        unique_transition_count=int(labels.nunique()) if not labels.empty else 0,
        most_common_transition=_most_common(labels) if not labels.empty else "NO_TRANSITION_DATA",
        directional_to_directional_count=_count_transition_family(from_states, to_states, "DIRECTIONAL", "DIRECTIONAL"),
        directional_to_rotation_count=_count_transition_family(from_states, to_states, "DIRECTIONAL", "ROTATION"),
        rotation_to_directional_count=_count_transition_family(from_states, to_states, "ROTATION", "DIRECTIONAL"),
        sample_transition_diagnostic=(
            "Partial sample generated transition context." if run.run_status == "COMPLETED" else run.run_diagnostic
        ),
    )


def load_price_outcome_summary(
    candidate: PartialCandidate,
    run: PartialValidationRunSummary,
    config: H4TargetedPartialExpansionValidationConfig,
) -> PartialPriceOutcomeSummary:
    frame = read_optional_csv(
        config.research_output_dir / candidate.candidate_id / "research" / "condition_price_outcome_summary.csv"
    )
    constrained = _count_truthy(frame, ["Low_Sample_Size", "low_sample_size"])
    ready = count_false_like(frame, ["Low_Sample_Size", "low_sample_size"])
    return PartialPriceOutcomeSummary(
        candidate_id=candidate.candidate_id,
        sample_label=candidate.sample_label,
        condition_profile_count=len(frame),
        research_ready_profile_count=ready,
        sample_constrained_profile_count=constrained,
        scenario_sensitive_profile_count=0,
        average_forward_range_pips=round(mean_column(frame, ["Average_Forward_Range_Pips", "average_forward_range_pips"]), 4),
        average_outcome_magnitude_pips=round(
            mean_column(frame, ["Average_Outcome_Magnitude_Pips", "average_outcome_magnitude_pips"]),
            4,
        ),
        average_direction_alignment_rate=round(
            mean_column(
                frame,
                [
                    "Direction_Alignment_Rate",
                    "direction_alignment_rate",
                    "Average_Direction_Alignment_Rate",
                    "average_direction_alignment_rate",
                ],
            ),
            4,
        ),
        price_outcome_diagnostic=(
            "Partial sample generated price outcome context." if run.run_status == "COMPLETED" else run.run_diagnostic
        ),
    )


def _most_common(values: pd.Series) -> str:
    counts = Counter(str(value) for value in values.dropna())
    if not counts:
        return ""
    return counts.most_common(1)[0][0]


def _state_diversity(unique_state_count: int) -> str:
    if unique_state_count >= 3:
        return "DIVERSE_STATE_SAMPLE"
    if unique_state_count >= 1:
        return "LIMITED_STATE_DIVERSITY"
    return "NO_STATE_DATA"


def _count_transition_family(from_states: pd.Series, to_states: pd.Series, source: str, target: str) -> int:
    if from_states.empty or to_states.empty:
        return 0
    count = 0
    for from_state, to_state in zip(from_states, to_states):
        if source in str(from_state).upper() and target in str(to_state).upper():
            count += 1
    return count


def _count_truthy(frame: pd.DataFrame, aliases: list[str]) -> int:
    column = resolve_column(frame, aliases)
    if column is None or frame.empty:
        return 0
    return int(frame[column].map(lambda raw: str(raw).strip().lower() in {"true", "1", "yes"}).sum())
