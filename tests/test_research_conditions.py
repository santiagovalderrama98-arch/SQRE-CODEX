from __future__ import annotations

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.loader import load_research_states, load_research_transitions
from tests.research_test_utils import write_sample_inputs


def test_research_conditions_include_states_transitions_tags_and_sequences(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)

    conditions = generate_research_conditions(
        states,
        transitions,
        ResearchEngineConfig(sequence_length=3),
    )

    condition_keys = {(condition.condition_type, condition.condition_value) for condition in conditions}
    assert ("STATE_CONDITION", "A") in condition_keys
    assert ("TRANSITION_CONDITION", "A -> B") in condition_keys
    assert ("TAG_CONDITION", "LOW_MAGNITUDE") in condition_keys
    assert ("SEQUENCE_CONDITION", "A -> B -> A") in condition_keys
    assert conditions[0].condition_id == "COND_000001"
