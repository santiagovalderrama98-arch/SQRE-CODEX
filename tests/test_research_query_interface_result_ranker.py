import pandas as pd

from sqre.research_query_interface_design.query_result_ranker import rank_reference_candidates


def test_ranker_prefers_core_reference_with_larger_sample():
    frame = pd.DataFrame(
        [
            {"Reference_Tier": "SUPPORTING_REFERENCE", "Outcome_Sample_Size": 100, "Outcome_Dispersion_Pips": 1},
            {"Reference_Tier": "CORE_REFERENCE", "Outcome_Sample_Size": 20, "Outcome_Dispersion_Pips": 5},
        ]
    )

    ranked = rank_reference_candidates(frame)

    assert ranked.iloc[0]["Reference_Tier"] == "CORE_REFERENCE"

