from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import H4TransitionStateCombinedContextReviewConfig
from sqre.h4_transition_state_combined_context_review.h4_transition_state_combined_context_review_pipeline import (
    run_h4_transition_state_combined_context_review,
)


def test_pipeline_handles_missing_inputs_without_failure(tmp_path: Path):
    config = H4TransitionStateCombinedContextReviewConfig(
        h4_state_deep_dive_dir=tmp_path / "empty_state_deep",
        h4_state_dispersion_dir=tmp_path / "empty_state_dispersion",
        h4_state_sensitive_dir=tmp_path / "empty_state_sensitive",
        h4_transition_deep_dive_dir=tmp_path / "empty_transition_deep",
        h4_transition_dispersion_dir=tmp_path / "empty_transition_dispersion",
        h4_transition_sensitive_dir=tmp_path / "empty_transition_sensitive",
        partial_complement_dir=tmp_path / "empty_partial_complement",
        partial_validation_dir=tmp_path / "empty_partial_validation",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )

    result = run_h4_transition_state_combined_context_review(config)

    assert result.summary is not None
    assert result.summary.context_count == 1
    assert result.report_path.exists()
    assert result.context_inventory[0].transition_profile_status == "TRANSITION_PROFILE_UNAVAILABLE"
