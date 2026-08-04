from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.findings import classify_readiness


def test_findings_produce_correct_readiness_flag():
    readiness, _, follow_up = classify_readiness(
        ready_count=1,
        moderate_count=0,
        low_or_insufficient_count=2,
        profile_count=3,
    )

    assert readiness == "PARTIAL_READY_FOR_H4_D1_OUTCOME_INTERPRETATION_REVIEW"
    assert follow_up == "OUTCOME_INTERPRETATION_REVIEW"
