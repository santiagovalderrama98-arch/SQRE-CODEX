from pathlib import Path

import pandas as pd

from test_h4_transition_outcome_deep_dive_loader import write_transition_inputs
from sqre.h4_transition_outcome_deep_dive.h4_transition_outcome_deep_dive_pipeline import run_h4_transition_outcome_deep_dive


EXPECTED_OUTPUTS = [
    "h4_transition_deep_dive_profile_inventory.csv",
    "h4_transition_scenario_breakdown.csv",
    "h4_transition_outcome_statistics.csv",
    "h4_transition_scenario_comparison_matrix.csv",
    "h4_transition_family_summary.csv",
    "h4_transition_deep_dive_summary.csv",
]


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "output"
    report_path = output_dir / "h4_transition_outcome_deep_dive_report.txt"
    write_transition_inputs(research_dir, validation_dir)

    result = run_h4_transition_outcome_deep_dive(research_dir, validation_dir, output_dir, report_path)

    assert len(result.selected_profiles) == 3
    assert len(result.scenario_breakdown_rows) == 6
    assert len(result.outcome_statistics_rows) == 3
    assert len(result.comparison_rows) == 6
    assert len(result.family_summary_rows) >= 1
    assert len(result.summary_rows) == 3
    for filename in EXPECTED_OUTPUTS:
        assert (output_dir / filename).exists()
    assert report_path.exists()

    inventory = pd.read_csv(output_dir / "h4_transition_deep_dive_profile_inventory.csv")
    assert "Source_State" in inventory.columns
    assert "Transition_Family" in inventory.columns
