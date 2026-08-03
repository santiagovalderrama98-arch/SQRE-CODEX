from sqre.h4_d1_temporal_alignment_feasibility_review.findings import (
    descriptive_findings,
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)


def test_findings_are_feasibility_only_and_non_operational():
    text = "\n".join(
        descriptive_findings(None) + potential_follow_up_areas() + do_not_change_yet_lines() + limitation_lines()
    ).lower()

    assert "feasibility" in text
    assert "no data was downloaded" in text
    assert "no operational logic was added" in text
    assert "no decision engine was added" in text
    assert "generate h4 timestamped context table" in text
