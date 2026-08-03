from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.loader import load_transition_alignment
from tests.h4_d1_same_time_contextual_transition_test_utils import write_transition_alignment


def test_loader_handles_missing_inputs_safely(tmp_path):
    assert load_transition_alignment(tmp_path / "missing").empty


def test_loader_loads_transition_same_time_alignment_table(tmp_path):
    write_transition_alignment(tmp_path)

    frame = load_transition_alignment(tmp_path)

    assert len(frame) == 24
    assert "H4_Transition_Label" in frame.columns
    assert "D1_Market_State" in frame.columns
