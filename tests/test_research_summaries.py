from __future__ import annotations

from sqre.research_engine.conditions import generate_research_conditions
from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.forward_analysis import analyze_forward_states, analyze_forward_transitions
from sqre.research_engine.loader import load_research_states, load_research_transitions
from sqre.research_engine.preceding_analysis import analyze_preceding_states
from sqre.research_engine.sequence_analysis import analyze_sequence_outcomes
from sqre.research_engine.summaries import build_condition_summaries
from tests.research_test_utils import write_sample_inputs


def test_research_summaries_build_condition_rollups(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)
    config = ResearchEngineConfig(forward_windows=[1], minimum_sample_size=3)
    conditions = generate_research_conditions(states, transitions, config)

    summaries = build_condition_summaries(
        conditions=conditions,
        forward_state_rows=analyze_forward_states(states, conditions, config),
        forward_transition_rows=analyze_forward_transitions(transitions, conditions, config),
        preceding_state_rows=analyze_preceding_states(states, conditions, config),
        sequence_outcome_rows=analyze_sequence_outcomes(states, conditions, config),
        config=config,
    )

    a_summary = next(row for row in summaries if row.condition_type == "STATE_CONDITION" and row.condition_value == "A")
    assert a_summary.sample_size == 2
    assert a_summary.forward_state_diversity == 2
    assert a_summary.low_sample_size is True
