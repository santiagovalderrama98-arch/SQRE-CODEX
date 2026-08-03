import pandas as pd

from sqre.h4_d1_same_time_alignment_table.alignment_coverage_review import build_alignment_coverage_review
from sqre.h4_d1_same_time_alignment_table.config import H4D1SameTimeAlignmentConfig


def _alignment(methods: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"Alignment_Method": methods})


def test_coverage_review_classifies_full_coverage():
    row = build_alignment_coverage_review(
        _alignment(["D1_INTERVAL_CONTAINMENT_MATCH", "D1_DATE_MATCH"]),
        _alignment(["D1_INTERVAL_CONTAINMENT_MATCH"]),
        pd.DataFrame({"D1_State_ID": ["D1_STATE_000001"]}),
        H4D1SameTimeAlignmentConfig(),
    )

    assert row.transition_alignment_coverage_class == "FULL_SAME_TIME_ALIGNMENT_COVERAGE"
    assert row.state_alignment_coverage_class == "FULL_SAME_TIME_ALIGNMENT_COVERAGE"
    assert row.overall_alignment_coverage_class == "FULL_SAME_TIME_ALIGNMENT_COVERAGE"


def test_coverage_review_classifies_partial_and_low_coverage():
    row = build_alignment_coverage_review(
        _alignment(["D1_INTERVAL_CONTAINMENT_MATCH", "NO_D1_SAME_TIME_MATCH"]),
        _alignment(["NO_D1_SAME_TIME_MATCH", "NO_D1_SAME_TIME_MATCH", "NO_D1_SAME_TIME_MATCH"]),
        pd.DataFrame({"D1_State_ID": ["D1_STATE_000001"]}),
        H4D1SameTimeAlignmentConfig(),
    )

    assert row.transition_alignment_coverage_class == "PARTIAL_SAME_TIME_ALIGNMENT_COVERAGE"
    assert row.state_alignment_coverage_class == "NO_SAME_TIME_ALIGNMENT_COVERAGE"
    assert row.overall_alignment_coverage_class == "NO_SAME_TIME_ALIGNMENT_COVERAGE"


def test_coverage_review_classifies_input_missing():
    row = build_alignment_coverage_review(
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        H4D1SameTimeAlignmentConfig(),
    )

    assert row.overall_alignment_coverage_class == "INPUT_MISSING"
