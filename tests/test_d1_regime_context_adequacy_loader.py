from __future__ import annotations

import pandas as pd

from sqre.d1_regime_context_adequacy_review.loader import load_profiles, read_optional_csv


def test_loader_normalizes_missing_profile_columns(tmp_path):
    input_dir = tmp_path / "contextual"
    input_dir.mkdir()
    pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A -> B",
                "Context_Row_Count": "7",
            }
        ]
    ).to_csv(input_dir / "h4_d1_same_time_contextual_transition_profiles.csv", index=False)

    frame = load_profiles(input_dir)

    assert frame.loc[0, "Context_Row_Count"] == 7
    assert frame.loc[0, "Transition_Total_Count"] == 0
    assert frame.loc[0, "D1_Market_State"] == ""


def test_read_optional_csv_returns_empty_for_missing_file(tmp_path):
    assert read_optional_csv(tmp_path / "missing.csv").empty
