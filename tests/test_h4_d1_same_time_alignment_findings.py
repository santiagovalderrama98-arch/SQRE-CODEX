from sqre.h4_d1_same_time_alignment_table.config import H4D1SameTimeAlignmentConfig
from sqre.h4_d1_same_time_alignment_table.alignment_coverage_review import build_alignment_coverage_review
from sqre.h4_d1_same_time_alignment_table.findings import build_summary, do_not_change_yet_lines

import pandas as pd


def test_findings_ready_when_full_coverage():
    coverage = build_alignment_coverage_review(
        pd.DataFrame({"Alignment_Method": ["D1_INTERVAL_CONTAINMENT_MATCH"]}),
        pd.DataFrame({"Alignment_Method": ["D1_INTERVAL_CONTAINMENT_MATCH"]}),
        pd.DataFrame({"D1_State_ID": ["D1_STATE_000001"]}),
        H4D1SameTimeAlignmentConfig(),
    )

    summary = build_summary(coverage)

    assert summary.h4_d1_same_time_alignment_readiness_flag == "READY_FOR_H4_D1_SAME_TIME_CONTEXTUAL_REVIEW"
    assert "No Decision Engine was added." in do_not_change_yet_lines()


def test_findings_input_completeness_review_when_input_missing():
    coverage = build_alignment_coverage_review(
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        H4D1SameTimeAlignmentConfig(),
    )

    summary = build_summary(coverage)

    assert summary.h4_d1_same_time_alignment_readiness_flag == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
