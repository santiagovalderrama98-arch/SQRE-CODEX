from pathlib import Path

from sqre.h4_d1_same_time_alignment_table.loader import (
    load_candle_alignment_map,
    load_d1_states,
    load_h4_states,
    load_h4_transitions,
)
from tests.h4_d1_same_time_alignment_test_utils import write_same_time_alignment_fixture


def test_loader_handles_missing_inputs_safely(tmp_path: Path):
    missing = tmp_path / "missing"

    assert load_h4_transitions(missing).empty
    assert load_h4_states(missing).empty
    assert load_d1_states(missing).empty
    assert load_candle_alignment_map(missing).empty


def test_loader_reads_all_alignment_inputs(tmp_path: Path):
    timestamped_dir, synchronized_dir = write_same_time_alignment_fixture(tmp_path)

    assert len(load_h4_transitions(timestamped_dir)) == 2
    assert len(load_h4_states(timestamped_dir)) == 3
    assert len(load_d1_states(timestamped_dir)) == 2
    assert len(load_candle_alignment_map(synchronized_dir)) == 1
