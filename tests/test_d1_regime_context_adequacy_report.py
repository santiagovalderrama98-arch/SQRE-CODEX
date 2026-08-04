from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.d1_regime_context_adequacy_pipeline import (
    D1RegimeContextAdequacyPipeline,
)
from sqre.d1_regime_context_adequacy_review.reports import FORBIDDEN_REPORT_TERMS, build_report_text
from tests.d1_regime_context_adequacy_test_utils import (
    write_contextual_transition_inputs,
    write_optional_supporting_inputs,
)


def test_report_writes_scope_and_avoids_forbidden_terms(tmp_path):
    contextual_dir = tmp_path / "contextual"
    alignment_dir = tmp_path / "alignment"
    timestamped_dir = tmp_path / "timestamped"
    output_dir = tmp_path / "out"
    write_contextual_transition_inputs(contextual_dir)
    write_optional_supporting_inputs(alignment_dir, timestamped_dir)
    result = D1RegimeContextAdequacyPipeline(
        D1RegimeContextAdequacyReviewConfig(
            contextual_transition_dir=contextual_dir,
            same_time_alignment_dir=alignment_dir,
            timestamped_state_regime_dir=timestamped_dir,
            output_dir=output_dir,
            report_path=output_dir / "report.txt",
        )
    ).run()

    text = build_report_text(result)

    assert "SQRE D1 Regime Context Adequacy Review" in text
    assert "This phase reviews D1 context adequacy only." in text
    assert all(term not in text.lower() for term in FORBIDDEN_REPORT_TERMS)
