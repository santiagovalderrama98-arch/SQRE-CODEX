from __future__ import annotations

from sqre.price_outcome_research.conditions import generate_price_outcome_conditions
from sqre.price_outcome_research.loader import (
    load_price_outcome_states,
    load_price_outcome_transitions,
)
from tests.price_outcome_test_utils import write_price_outcome_inputs


def test_price_outcome_conditions_are_states_and_transitions_only(tmp_path) -> None:
    states_path, transitions_path, _ = write_price_outcome_inputs(tmp_path)
    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)

    conditions = generate_price_outcome_conditions(states, transitions)
    keys = {(condition.condition_type, condition.condition_value) for condition in conditions}

    assert ("STATE_CONDITION", "A") in keys
    assert ("STATE_CONDITION", "B") in keys
    assert ("TRANSITION_CONDITION", "A -> B") in keys
    assert conditions[0].condition_id == "COND_000001"
    assert len(keys) == len(conditions)
    assert "TAG_CONDITION" not in {condition.condition_type for condition in conditions}
    assert "SEQUENCE_CONDITION" not in {condition.condition_type for condition in conditions}
