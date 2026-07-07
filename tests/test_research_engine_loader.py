from __future__ import annotations

import pandas as pd
import pytest

from sqre.research_engine.loader import load_research_states, load_research_transitions
from tests.research_test_utils import write_sample_inputs


def test_research_engine_loader_reads_states_and_transitions(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)

    states = load_research_states(states_path)
    transitions = load_research_transitions(transitions_path)

    assert len(states) == 6
    assert len(transitions) == 5
    assert states[0].state_id == "S1"
    assert transitions[0].transition_label == "A -> B"


def test_research_engine_loader_validates_required_columns(tmp_path) -> None:
    states_path = tmp_path / "bad_states.csv"
    pd.DataFrame({"State_ID": ["S1"]}).to_csv(states_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_research_states(states_path)
