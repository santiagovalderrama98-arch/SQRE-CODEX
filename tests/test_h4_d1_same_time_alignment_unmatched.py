import pandas as pd

from sqre.h4_d1_same_time_alignment_table.unmatched_alignment_review import build_unmatched_alignment_review


def test_unmatched_review_recommends_no_action_when_all_matched():
    rows = build_unmatched_alignment_review(
        pd.DataFrame({"Alignment_Method": ["D1_INTERVAL_CONTAINMENT_MATCH"]}),
        pd.DataFrame({"Alignment_Method": ["D1_DATE_MATCH"]}),
        d1_state_count=1,
    )

    assert rows[0].required_source_action == "NO_ACTION_REQUIRED"


def test_unmatched_review_recommends_d1_coverage_when_d1_missing():
    transition_alignment = pd.DataFrame(
        {
            "Alignment_Method": ["NO_D1_SAME_TIME_MATCH"],
            "H4_Transition_ID": ["H4_TRN_000001"],
            "H4_Transition_Time": ["2026-07-01 04:00:00"],
            "H4_Transition_Date": ["2026-07-01"],
        }
    )

    rows = build_unmatched_alignment_review(transition_alignment, pd.DataFrame(), d1_state_count=0)

    assert rows[0].required_source_action == "REVIEW_D1_TIMESTAMPED_STATE_COVERAGE"


def test_unmatched_review_recommends_h4_timestamp_review_when_timestamp_missing():
    state_alignment = pd.DataFrame(
        {
            "Alignment_Method": ["NO_D1_SAME_TIME_MATCH"],
            "H4_State_ID": ["H4_STATE_000001"],
            "H4_State_Event_Time": [""],
            "H4_State_Event_Date": ["2026-07-01"],
        }
    )

    rows = build_unmatched_alignment_review(pd.DataFrame(), state_alignment, d1_state_count=1)

    assert rows[0].required_source_action == "REVIEW_H4_STATE_TIMESTAMPS"
