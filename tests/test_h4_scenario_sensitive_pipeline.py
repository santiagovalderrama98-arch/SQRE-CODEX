from pathlib import Path

from test_h4_scenario_sensitive_state_review_loader import write_sensitive_inputs
from sqre.h4_scenario_sensitive_state_review.h4_scenario_sensitive_state_review_pipeline import (
    run_h4_scenario_sensitive_state_review,
)


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    dispersion_dir, deep_dive_dir = write_sensitive_inputs(tmp_path)

    result = run_h4_scenario_sensitive_state_review(
        dispersion_dir,
        deep_dive_dir,
        tmp_path / "out",
        tmp_path / "out" / "h4_scenario_sensitive_state_review_report.txt",
    )

    assert len(result.reviewed_profiles) == 3
    assert len(result.scenario_details) == 9
    assert len(result.scenario_summaries) == 3
    assert len(result.state_summaries) == 3
    assert len(result.window_summaries) == 2
    assert len(result.near_candidates) == 2
    for name in [
        "h4_scenario_sensitive_profile_review.csv",
        "h4_profile_scenario_deviation_detail.csv",
        "h4_scenario_recurrent_deviation_summary.csv",
        "h4_state_sensitivity_summary.csv",
        "h4_forward_window_sensitivity_summary.csv",
        "h4_near_aggregation_candidate_review.csv",
        "h4_scenario_sensitive_state_review_summary.csv",
    ]:
        assert (result.output_dir / name).exists()
    assert result.report_path.exists()
