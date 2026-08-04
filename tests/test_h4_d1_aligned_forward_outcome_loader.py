from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.loader import load_h4_ohlc, load_transition_alignment
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_loader_handles_missing_inputs_safely(tmp_path):
    assert load_transition_alignment(tmp_path / "missing").empty
    assert load_h4_ohlc(tmp_path / "missing").empty


def test_loader_loads_alignment_and_h4_ohlc(tmp_path):
    alignment_dir, synchronized_dir, _ = write_forward_outcome_inputs(tmp_path)

    alignment = load_transition_alignment(alignment_dir)
    h4 = load_h4_ohlc(synchronized_dir)

    assert len(alignment) == 2
    assert len(h4) == 7
    assert "Timestamp" in h4.columns
