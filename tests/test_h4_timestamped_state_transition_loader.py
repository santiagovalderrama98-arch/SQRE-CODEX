from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_state_transition_outputs.loader import read_optional_csv, resolve_column, row_text


def test_loader_handles_missing_optional_inputs_safely(tmp_path: Path):
    assert read_optional_csv(tmp_path / "missing.csv").empty


def test_loader_resolves_columns_case_insensitively():
    frame = pd.DataFrame({"condition_label": ["A"]})

    assert resolve_column(frame, ["Condition_Label"]) == "condition_label"
    assert row_text(frame.iloc[0], ["Condition_Label"]) == "A"
