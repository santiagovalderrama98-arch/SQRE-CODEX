from pathlib import Path

import pandas as pd

from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_transition_scenario_dispersion_review.h4_transition_scenario_dispersion_review_pipeline import run_h4_transition_scenario_dispersion_review


EXPECTED_OUTPUTS = [
    "h4_transition_profile_dispersion_diagnostics.csv",
    "h4_transition_scenario_dispersion_contribution.csv",
    "h4_transition_family_dispersion_summary.csv",
    "h4_transition_source_state_dispersion_summary.csv",
    "h4_transition_target_state_dispersion_summary.csv",
    "h4_transition_forward_window_dispersion_summary.csv",
    "h4_transition_aggregation_candidate_profiles.csv",
    "h4_transition_scenario_sensitive_profiles.csv",
    "h4_transition_sample_constrained_profiles.csv",
    "h4_transition_scenario_dispersion_review_summary.csv",
]


def test_pipeline_writes_all_expected_outputs_and_subsets(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    report_path = output_dir / "report.txt"
    write_review_inputs(input_dir)

    result = run_h4_transition_scenario_dispersion_review(input_dir, output_dir, report_path)

    assert len(result.profile_diagnostics) == 4
    assert len(result.scenario_contributions) == 3
    assert len(result.family_summaries) == 2
    assert len(result.source_state_summaries) == 3
    assert len(result.target_state_summaries) == 2
    assert len(result.window_summaries) == 3
    assert len(result.aggregation_candidates) >= 1
    assert len(result.scenario_sensitive_profiles) >= 1
    assert len(result.sample_constrained_profiles) == 1
    for filename in EXPECTED_OUTPUTS:
        assert (output_dir / filename).exists()
    summary = pd.read_csv(output_dir / "h4_transition_scenario_dispersion_review_summary.csv")
    assert summary.loc[0, "Timeframe"] == "H4"
    assert report_path.exists()
