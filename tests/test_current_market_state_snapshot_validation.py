import pandas as pd

from sqre.current_market_state_snapshot_research.snapshot_validation import validate_snapshot_context


def test_validation_requires_h4_transition():
    status, _ = validate_snapshot_context(pd.Series({"Snapshot_Source": "USER_SUPPLIED_CONTEXT"}))

    assert status == "INVALID_SNAPSHOT_CONTEXT"


def test_validation_marks_partial_when_d1_context_is_missing():
    status, _ = validate_snapshot_context(pd.Series({"Snapshot_Source": "USER_SUPPLIED_CONTEXT", "H4_Transition_Label": "A"}))

    assert status == "PARTIAL_SNAPSHOT_CONTEXT"


def test_validation_marks_input_missing():
    status, _ = validate_snapshot_context(pd.Series({"Snapshot_Source": "INPUT_MISSING"}))

    assert status == "INPUT_MISSING"
