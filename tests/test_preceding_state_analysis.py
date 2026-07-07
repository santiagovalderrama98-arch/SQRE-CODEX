from __future__ import annotations

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.loader import load_research_states, load_research_transitions
from sqre.research_engine.preceding_analysis import analyze_preceding_states
from tests.research_test_utils import write_sample_inputs


def test_preceding_state_analysis_counts_previous_states(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)
    config = ResearchEngineConfig()
    conditions = generate_research_conditions(states, transitions, config)

    rows = analyze_preceding_states(states, conditions, config)
    a_rows = [row for row in rows if row.condition_value == "A"]

    assert {row.observed_preceding_state for row in a_rows} == {"B"}
    assert sum(row.count for row in a_rows) == 2
    assert all(row.sample_size == 2 for row in a_rows)
