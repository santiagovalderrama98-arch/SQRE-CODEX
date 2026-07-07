from __future__ import annotations

from sqre.price_outcome_research.conditions import generate_price_outcome_conditions
from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.loader import (
    load_ohlc,
    load_price_outcome_states,
    load_price_outcome_transitions,
)
from sqre.price_outcome_research.outcomes import (
    build_price_outcomes,
    calculate_price_outcome_for_occurrence,
)
from tests.price_outcome_test_utils import write_price_outcome_inputs


def test_state_condition_outcome_metrics_for_up_direction(tmp_path) -> None:
    states_path, transitions_path, ohlc_path = write_price_outcome_inputs(tmp_path)
    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)
    candles = load_ohlc(ohlc_path)
    condition = next(
        condition
        for condition in generate_price_outcome_conditions(states, transitions)
        if condition.condition_type == "STATE_CONDITION" and condition.condition_value == "C"
    )

    row = calculate_price_outcome_for_occurrence(
        condition,
        states[-1],
        candles,
        2,
        PriceOutcomeResearchConfig(forward_candles=[2]),
    )

    assert row is not None
    assert row.occurrence_id == "S4"
    assert row.reference_time == states[-1].end_time
    assert row.reference_close == 1.1030
    assert round(row.forward_close_return_pips, 4) == 5.0
    assert round(row.forward_range_pips, 4) == 30.0
    assert round(row.max_favorable_displacement_pips, 4) == 20.0
    assert round(row.max_adverse_displacement_pips, 4) == 10.0
    assert row.direction_aligned is True
    assert row.positive_close_return is True
    assert row.complete_forward_window is True


def test_transition_condition_uses_to_direction_for_down_direction(tmp_path) -> None:
    states_path, transitions_path, ohlc_path = write_price_outcome_inputs(tmp_path)
    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)
    candles = load_ohlc(ohlc_path)
    condition = next(
        condition
        for condition in generate_price_outcome_conditions(states, transitions)
        if condition.condition_type == "TRANSITION_CONDITION" and condition.condition_value == "A -> B"
    )

    row = calculate_price_outcome_for_occurrence(
        condition,
        transitions[0],
        candles,
        1,
        PriceOutcomeResearchConfig(forward_candles=[1]),
    )

    assert row is not None
    assert row.occurrence_id == "T1"
    assert row.direction == "DOWN"
    assert round(row.forward_close_return_pips, 4) == -10.0
    assert row.direction_aligned is True
    assert row.negative_close_return is True
    assert round(row.max_favorable_displacement_pips, 4) == 15.0
    assert round(row.max_adverse_displacement_pips, 4) == 5.0


def test_neutral_direction_and_incomplete_forward_window(tmp_path) -> None:
    states_path, transitions_path, ohlc_path = write_price_outcome_inputs(tmp_path)
    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)
    candles = load_ohlc(ohlc_path)
    condition = next(
        condition
        for condition in generate_price_outcome_conditions(states, transitions)
        if condition.condition_type == "STATE_CONDITION" and condition.condition_value == "A"
    )

    row = calculate_price_outcome_for_occurrence(
        condition,
        states[2],
        candles,
        5,
        PriceOutcomeResearchConfig(forward_candles=[5]),
    )

    assert row is not None
    assert row.direction == "NEUTRAL"
    assert row.direction_aligned is False
    assert row.complete_forward_window is False
    assert row.max_favorable_displacement_pips == row.max_adverse_displacement_pips


def test_build_price_outcomes_assigns_ids_and_skips_missing_forward_candles(tmp_path) -> None:
    states_path, transitions_path, ohlc_path = write_price_outcome_inputs(tmp_path)
    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)
    candles = load_ohlc(ohlc_path)
    conditions = generate_price_outcome_conditions(states, transitions)

    rows = build_price_outcomes(
        states,
        transitions,
        candles,
        conditions,
        PriceOutcomeResearchConfig(forward_candles=[1]),
    )

    assert rows[0].outcome_id == "OUT_000001"
    assert all(row.forward_window_candles == 1 for row in rows)
