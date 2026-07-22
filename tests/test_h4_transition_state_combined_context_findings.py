from sqre.h4_transition_state_combined_context_review.config import H4TransitionStateCombinedContextReviewConfig
from sqre.h4_transition_state_combined_context_review.findings import build_summary
from sqre.h4_transition_state_combined_context_review.models import CombinedContextInterpretationRow


def test_findings_build_summary_counts_readiness():
    row = CombinedContextInterpretationRow(
        "CTX_1",
        "EURUSD",
        "H4",
        "A",
        "B",
        "A -> B",
        "12",
        "STATE_TRANSITION_ALIGNED_SAMPLE_CONSTRAINED",
        "COMBINED_SAMPLE_CONSTRAINED",
        "COMBINED_SAMPLE_CONSTRAINED",
        "PARTIAL_CONTEXT_UNAVAILABLE",
        "CONTEXT_SAMPLE_CONSTRAINED",
        "REQUIRES_SAMPLE_ADEQUACY_REVIEW",
        "sample constrained",
        "Provider history coverage review",
    )

    summary = build_summary([row], H4TransitionStateCombinedContextReviewConfig())

    assert summary.context_count == 1
    assert summary.requires_sample_adequacy_review_count == 1
    assert summary.h4_transition_state_context_readiness_flag == "H4_CONTEXT_REQUIRES_SAMPLE_ADEQUACY_REVIEW"
