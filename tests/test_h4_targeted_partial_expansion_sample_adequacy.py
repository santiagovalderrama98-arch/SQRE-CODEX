from sqre.h4_targeted_partial_expansion_validation.sample_adequacy_review import classify_sample_adequacy


def test_sample_adequacy_research_usable():
    assert classify_sample_adequacy("FOUND", 0.5, 100, 20, 20, 10) == "PARTIAL_SAMPLE_RESEARCH_USABLE"


def test_sample_adequacy_limited():
    assert classify_sample_adequacy("FOUND", 0.3, 100, 10, 5, 2) == "PARTIAL_SAMPLE_LIMITED"


def test_sample_adequacy_unavailable():
    assert classify_sample_adequacy("MISSING", 0.9, 0, 0, 0, 0) == "PARTIAL_SAMPLE_UNAVAILABLE"


def test_sample_adequacy_insufficient():
    assert classify_sample_adequacy("FOUND", 0.2, 100, 5, 5, 1) == "PARTIAL_SAMPLE_INSUFFICIENT"
