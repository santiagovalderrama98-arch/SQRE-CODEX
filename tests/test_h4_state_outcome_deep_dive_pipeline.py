from pathlib import Path

import pandas as pd

from h4_state_deep_dive_test_utils import write_h4_deep_dive_inputs
from sqre.h4_state_outcome_deep_dive.h4_state_outcome_deep_dive_pipeline import run_h4_state_outcome_deep_dive


EXPECTED_OUTPUTS = [
    "h4_state_deep_dive_profile_inventory.csv",
    "h4_state_scenario_breakdown.csv",
    "h4_state_outcome_statistics.csv",
    "h4_state_scenario_comparison_matrix.csv",
    "h4_state_deep_dive_summary.csv",
]


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    research_dir = tmp_path / "research"
    validation_dir = tmp_path / "validation"
    output_dir = tmp_path / "output"
    report_path = output_dir / "h4_state_outcome_deep_dive_report.txt"
    write_h4_deep_dive_inputs(research_dir, validation_dir)

    result = run_h4_state_outcome_deep_dive(research_dir, validation_dir, output_dir, report_path)

    assert len(result.selected_profiles) == 3
    assert len(result.scenario_breakdown_rows) == 6
    assert len(result.outcome_statistics_rows) == 3
    assert len(result.comparison_rows) == 6
    assert len(result.summary_rows) == 3
    for filename in EXPECTED_OUTPUTS:
        assert (output_dir / filename).exists()
    assert report_path.exists()

    summary = pd.read_csv(output_dir / "h4_state_deep_dive_summary.csv")
    assert set(summary["Condition_Label"]) == {
        "DIRECTIONAL_DISPLACEMENT",
        "DIRECTIONAL_EXPANSION",
        "VOLATILE_ROTATION",
    }
