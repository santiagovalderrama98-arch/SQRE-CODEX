from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.h4_d1_same_time_contextual_transition_pipeline import (
    H4D1SameTimeContextualTransitionReviewPipeline,
)
from tests.h4_d1_same_time_contextual_transition_test_utils import write_transition_alignment


def test_pipeline_writes_expected_outputs(tmp_path):
    same_time_dir = tmp_path / "same_time"
    write_transition_alignment(same_time_dir)
    output_dir = tmp_path / "out"

    result = H4D1SameTimeContextualTransitionReviewPipeline(
        H4D1SameTimeContextualTransitionReviewConfig(
            same_time_alignment_dir=same_time_dir,
            timestamped_state_regime_dir=tmp_path / "optional",
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
        )
    ).run()

    assert result.summary is not None
    assert (output_dir / "h4_d1_same_time_contextual_transition_profiles.csv").exists()
    assert (output_dir / "h4_transition_d1_market_state_distribution.csv").exists()
    assert (output_dir / "h4_d1_same_time_contextual_transition_review_summary.csv").exists()
    assert result.report_path.exists()
