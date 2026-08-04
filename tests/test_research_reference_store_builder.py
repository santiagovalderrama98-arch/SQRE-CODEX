import pandas as pd

from sqre.research_reference_store_design.reference_store_builder import build_reference_store


def test_store_builder_writes_only_included_reference_rows():
    candidates = pd.DataFrame(
        [
            {
                "Outcome_Profile_ID": "OP_1",
                "Reference_Inclusion_Status": "INCLUDED_IN_RESEARCH_REFERENCE_STORE",
                "Reference_Diagnostic": "Included.",
                "Reference_Tier": "CORE_RESEARCH_REFERENCE",
            },
            {
                "Outcome_Profile_ID": "OP_2",
                "Reference_Inclusion_Status": "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE",
                "Reference_Diagnostic": "Excluded.",
                "Reference_Tier": "EXCLUDED_SAMPLE_CONSTRAINED",
            },
        ]
    )

    store = build_reference_store(candidates)

    assert store["Outcome_Profile_ID"].tolist() == ["OP_1"]
    assert store.iloc[0]["Research_Reference_ID"] == "RRS_000001"
