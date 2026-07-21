from pathlib import Path

from test_h4_transition_scenario_sensitive_review_loader import write_transition_sensitive_inputs
from sqre.h4_transition_scenario_sensitive_review.h4_transition_scenario_sensitive_review_pipeline import (
    run_h4_transition_scenario_sensitive_review,
)


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_transition_sensitive_inputs(tmp_path)

    result = run_h4_transition_scenario_sensitive_review(
        dispersion_dir,
        deep_dive_dir,
        tmp_path / "out",
        tmp_path / "out" / "h4_transition_scenario_sensitive_review_report.txt",
    )

    assert len(result.reviewed_profiles) == 3
    assert len(result.focus_profiles) == 2
    assert len(result.scenario_details) == 9
    assert len(result.scenario_summaries) == 3
    assert len(result.family_summaries) == 2
    assert len(result.source_state_summaries) == 2
    assert len(result.target_state_summaries) == 3
    assert len(result.window_summaries) == 2
    assert len(result.near_candidates) == 1
    for name in [
        "h4_transition_scenario_sensitive_profile_review.csv",
        "h4_transition_profile_scenario_deviation_detail.csv",
        "h4_transition_scenario_recurrent_deviation_summary.csv",
        "h4_transition_family_sensitivity_summary.csv",
        "h4_transition_source_state_sensitivity_summary.csv",
        "h4_transition_target_state_sensitivity_summary.csv",
        "h4_transition_forward_window_sensitivity_summary.csv",
        "h4_transition_near_aggregation_candidate_review.csv",
        "h4_transition_focus_profile_review.csv",
        "h4_transition_scenario_sensitive_review_summary.csv",
    ]:
        assert (result.output_dir / name).exists()
    assert result.report_path.exists()
