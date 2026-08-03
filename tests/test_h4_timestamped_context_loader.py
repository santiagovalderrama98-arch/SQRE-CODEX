from pathlib import Path

from sqre.h4_timestamped_context_table_generation.loader import read_optional_csv, resolve_column


def test_loader_handles_missing_optional_inputs_safely(tmp_path: Path):
    frame = read_optional_csv(tmp_path / "missing.csv")

    assert frame.empty
    assert resolve_column(frame, ["Scenario_ID"]) is None
