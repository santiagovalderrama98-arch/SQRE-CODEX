from __future__ import annotations

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.forward_analysis import analyze_forward_transitions
from sqre.research_engine.loader import load_research_states, load_research_transitions
from tests.research_test_utils import write_sample_inputs


def test_forward_transition_analysis_counts_next_transitions(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)
    config = ResearchEngineConfig(minimum_sample_size=2)
    conditions = generate_research_conditions(states, transitions, config)

    rows = analyze_forward_transitions(transitions, conditions, config)
    tag_rows = [row for row in rows if row.condition_type == "TAG_CONDITION" and row.condition_value == "LOW_MAGNITUDE"]

    assert tag_rows
    assert {row.observed_forward_transition for row in tag_rows} >= {"B -> A", "A -> C"}
    assert all(row.sample_size == 3 for row in tag_rows)
