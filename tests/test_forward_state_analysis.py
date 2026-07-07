from __future__ import annotations

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.forward_analysis import analyze_forward_states
from sqre.research_engine.loader import load_research_states, load_research_transitions
from tests.research_test_utils import write_sample_inputs


def test_forward_state_analysis_counts_following_states(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)
    config = ResearchEngineConfig(forward_windows=[1], minimum_sample_size=3)
    conditions = generate_research_conditions(states, transitions, config)

    rows = analyze_forward_states(states, conditions, config)
    a_rows = [row for row in rows if row.condition_value == "A" and row.forward_window == 1]

    assert {row.observed_forward_state for row in a_rows} == {"B", "C"}
    assert sum(row.count for row in a_rows) == 2
    assert all(row.sample_size == 2 for row in a_rows)
    assert all(row.low_sample_size for row in a_rows)
