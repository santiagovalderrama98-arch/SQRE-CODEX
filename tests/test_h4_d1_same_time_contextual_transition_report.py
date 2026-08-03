from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.h4_d1_same_time_contextual_transition_pipeline import (
    H4D1SameTimeContextualTransitionReviewPipeline,
)
from sqre.h4_d1_same_time_contextual_transition_review.reports import FORBIDDEN_REPORT_TERMS
from tests.h4_d1_same_time_contextual_transition_test_utils import write_transition_alignment


def test_report_includes_sections_and_excludes_forbidden_language(tmp_path):
    same_time_dir = tmp_path / "same_time"
    write_transition_alignment(same_time_dir)
    output_dir = tmp_path / "out"
    report_path = output_dir / "report.txt"

    result = H4D1SameTimeContextualTransitionReviewPipeline(
        H4D1SameTimeContextualTransitionReviewConfig(
            same_time_alignment_dir=same_time_dir,
            timestamped_state_regime_dir=tmp_path / "optional",
            output_dir=output_dir,
            report_path=report_path,
        )
    ).run()

    text = result.report_path.read_text()
    assert "Same-Time Contextual Transition Profiles" in text
    assert "This phase does not study forward price outcomes." in text
    assert "This phase prepares context profiles for later outcome research." in text
    lowered = text.lower()
    assert not [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
