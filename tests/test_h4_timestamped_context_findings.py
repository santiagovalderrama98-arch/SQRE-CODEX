from sqre.h4_timestamped_context_table_generation.findings import build_summary
from sqre.h4_timestamped_context_table_generation.models import CoverageReviewRow


def test_findings_classify_missing_readiness():
    coverage = [
        CoverageReviewRow("SCN_1", "EURUSD", "H4", "", "", 1, 0, 0, 0, 0, 0, 0.0, "NO_TEMPORAL_CONTEXT_COVERAGE", "")
    ]

    summary = build_summary([], coverage, [], "EURUSD", "H4")

    assert summary.h4_timestamped_context_readiness_flag == "NOT_READY_TIMESTAMPED_CONTEXT_MISSING"
    assert summary.recommended_follow_up == "GENERATE_STATE_TRANSITION_OUTPUTS_WITH_TIMESTAMPS"
