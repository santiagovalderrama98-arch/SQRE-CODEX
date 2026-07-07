from __future__ import annotations

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.loader import load_research_states, load_research_transitions
from sqre.research_engine.sequence_analysis import analyze_sequence_outcomes
from tests.research_test_utils import write_sample_inputs


def test_sequence_outcome_analysis_counts_following_state(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)
    config = ResearchEngineConfig(sequence_length=3, minimum_sample_size=2)
    conditions = generate_research_conditions(states, transitions, config)

    rows = analyze_sequence_outcomes(states, conditions, config)
    target_rows = [row for row in rows if row.sequence == "A -> B -> A"]

    assert len(target_rows) == 1
    assert target_rows[0].observed_forward_state == "C"
    assert target_rows[0].sample_size == 1
    assert target_rows[0].low_sample_size is True
