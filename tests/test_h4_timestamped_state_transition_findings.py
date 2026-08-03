from sqre.h4_timestamped_state_transition_outputs.findings import build_summary
from sqre.h4_timestamped_state_transition_outputs.models import CoverageReviewRow


def test_findings_classify_readiness_correctly():
    coverage = [
        CoverageReviewRow(
            "SCN_1",
            "EURUSD",
            "H4",
            "2026-01-01",
            "2026-01-31",
            1,
            1,
            1,
            1,
            1,
            1,
            1.0,
            1.0,
            "FULL_TIMESTAMPED_STATE_TRANSITION_COVERAGE",
            "full",
        )
    ]

    summary = build_summary([], coverage, [object()], [object()], [], "EURUSD", "H4")

    assert summary.h4_timestamped_state_transition_readiness_flag == "READY_FOR_H4_TIMESTAMPED_CONTEXT_TABLE"


def test_findings_classify_missing_outputs():
    summary = build_summary([], [], [], [], [], "EURUSD", "H4")

    assert summary.h4_timestamped_state_transition_readiness_flag == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
