import pandas as pd

from sqre.current_market_state_snapshot_research.snapshot_reference_ranker import rank_snapshot_reference_candidates


def test_ranker_prefers_core_larger_sample_lower_dispersion():
    candidates = pd.DataFrame(
        [
            {"Research_Reference_ID": "B", "Reference_Tier": "SUPPORTING_REFERENCE", "Outcome_Sample_Size": 100, "Outcome_Dispersion_Pips": 1},
            {"Research_Reference_ID": "A", "Reference_Tier": "CORE_REFERENCE", "Outcome_Sample_Size": 20, "Outcome_Dispersion_Pips": 10},
        ]
    )

    ranked = rank_snapshot_reference_candidates(candidates)

    assert ranked.iloc[0]["Research_Reference_ID"] == "A"
