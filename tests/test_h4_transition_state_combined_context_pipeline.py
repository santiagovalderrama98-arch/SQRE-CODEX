from pathlib import Path

from sqre.h4_transition_state_combined_context_review.config import H4TransitionStateCombinedContextReviewConfig
from sqre.h4_transition_state_combined_context_review.h4_transition_state_combined_context_review_pipeline import (
    run_h4_transition_state_combined_context_review,
)


def test_pipeline_handles_missing_inputs_without_failure(tmp_path: Path):
    config = H4TransitionStateCombinedContextReviewConfig(
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )

    result = run_h4_transition_state_combined_context_review(config)

    assert result.summary is not None
    assert result.summary.context_count == 1
    assert result.report_path.exists()
    assert result.context_inventory[0].transition_profile_status == "TRANSITION_PROFILE_UNAVAILABLE"
