from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.d1_context_inventory import build_d1_context_inventory
from sqre.d1_regime_context_adequacy_review.d1_fragmentation_review import build_fragmentation_review
from sqre.d1_regime_context_adequacy_review.findings import readiness_lines
from sqre.d1_regime_context_adequacy_review.h4_transition_sample_loss_review import build_sample_loss_review
from sqre.d1_regime_context_adequacy_review.readiness_classifier import build_summary
from tests.d1_regime_context_adequacy_test_utils import write_contextual_transition_inputs


def test_findings_include_readiness_and_follow_up(tmp_path):
    config = D1RegimeContextAdequacyReviewConfig()
    profiles = write_contextual_transition_inputs(tmp_path / "contextual")
    inventory = build_d1_context_inventory(profiles, config)
    fragmentation = build_fragmentation_review(profiles, __import__("pandas").DataFrame(), config)
    sample_loss = build_sample_loss_review(profiles, config)
    candidates = __import__("pandas").DataFrame({"Aggregation_Candidate_Class": ["INPUT_LIMITED"]})
    summary = build_summary(profiles, inventory, fragmentation, sample_loss, candidates, config)

    lines = "\n".join(readiness_lines(summary))

    assert "D1 regime context adequacy readiness flag" in lines
    assert "D1_REGIME_GROUPING_RESEARCH" in lines
