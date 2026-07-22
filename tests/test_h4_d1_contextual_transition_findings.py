from sqre.h4_d1_contextual_transition_review.findings import (
    do_not_change_yet_lines,
    limitation_lines,
    potential_follow_up_areas,
)


def test_findings_are_descriptive_and_non_operational():
    text = "\n".join(potential_follow_up_areas() + do_not_change_yet_lines() + limitation_lines()).lower()

    assert "no operational logic was added" in text
    assert "no data was downloaded" in text
    assert "partial sample was not silently merged" in text
