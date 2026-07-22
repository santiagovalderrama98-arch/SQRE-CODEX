from sqre.h4_targeted_partial_expansion_validation.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)


def test_findings_are_descriptive():
    text = "\n".join(potential_follow_up_areas() + do_not_change_yet_lines() + limitation_lines()).lower()

    assert "descriptive" in text
    assert "decision engine" not in text
    assert "signal" not in text
