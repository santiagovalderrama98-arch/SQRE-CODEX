from pathlib import Path

from sqre.h4_d1_contextual_transition_review.config import H4D1ContextualTransitionReviewConfig
from sqre.h4_d1_contextual_transition_review.h4_d1_contextual_transition_review_pipeline import (
    run_h4_d1_contextual_transition_review,
)
from sqre.h4_d1_contextual_transition_review.reports import FORBIDDEN_REPORT_TERMS


def test_report_includes_required_sections_and_excludes_forbidden_language(tmp_path: Path):
    config = H4D1ContextualTransitionReviewConfig(
        h4_combined_context_dir=tmp_path / "missing_h4",
        d1_regime_normalized_dir=tmp_path / "missing_d1_regime",
        d1_regime_outcome_review_dir=tmp_path / "missing_d1_outcome",
        d1_state_deep_dive_dir=tmp_path / "missing_d1_state",
        h4_d1_structural_research_dir=tmp_path / "missing_structural",
        h4_d1_validation_dir=tmp_path / "missing_validation",
        partial_complement_dir=tmp_path / "missing_partial",
        partial_validation_dir=tmp_path / "missing_partial_validation",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out" / "report.txt",
    )

    result = run_h4_d1_contextual_transition_review(config)
    text = result.report_path.read_text(encoding="utf-8")

    assert "H4/D1 Scenario Context Map" in text
    assert "Contextual Dispersion Review" in text
    assert "Do Not Change Yet" in text
    assert all(term not in text.lower() for term in FORBIDDEN_REPORT_TERMS)
