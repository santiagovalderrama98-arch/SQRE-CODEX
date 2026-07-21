from sqre.h4_expanded_sample_feasibility_review.findings import (
    constraint_diagnostic,
    feasibility_diagnostic,
    summary_diagnostic,
    summary_follow_up,
)


def test_findings_return_descriptive_text():
    assert "available" in feasibility_diagnostic("FEASIBLE_FULL_SAMPLE").lower()
    assert "coverage" in constraint_diagnostic("SAMPLE_AVAILABILITY_CONSTRAINED").lower()
    assert "candidates" in summary_diagnostic("EXPANSION_POSSIBLE", "NO_MAJOR_CONSTRAINT_IDENTIFIED").lower()
    assert "availability" in summary_follow_up("REQUIRES_DATA_AVAILABILITY_RESOLUTION").lower()
