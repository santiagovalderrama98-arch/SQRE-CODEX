import pandas as pd

from sqre.manual_research_dashboard_review.field_usefulness_review import build_field_usefulness_review


def test_field_usefulness_classifies_core_supporting_diagnostic_and_low_use_fields():
    frames = {
        "prototype_snapshot_panel": pd.DataFrame(
            [
                {
                    "Snapshot_Mode": "LATEST",
                    "Source_Name": "snapshot",
                    "Readiness_Diagnostic": "ok",
                    "Reference_Card_ID": "REF_1",
                }
            ]
        )
    }

    review = build_field_usefulness_review(frames)

    assert "CORE_RESEARCH_FIELD" in set(review["Field_Usefulness_Class"])
    assert "SUPPORTING_RESEARCH_FIELD" in set(review["Field_Usefulness_Class"])
    assert "DIAGNOSTIC_FIELD" in set(review["Field_Usefulness_Class"])
    assert "REDUNDANT_OR_LOW_USE_FIELD" in set(review["Field_Usefulness_Class"])
