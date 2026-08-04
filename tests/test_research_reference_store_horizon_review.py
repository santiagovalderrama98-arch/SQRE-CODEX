import pandas as pd

from sqre.research_reference_store_design.horizon_reference_review import build_horizon_reference_review


def test_horizon_review_identifies_primary_reference_horizon():
    candidates = pd.DataFrame(
        [
            _row(3, "CORE_RESEARCH_REFERENCE", "INCLUDED_IN_RESEARCH_REFERENCE_STORE"),
            _row(3, "SUPPORTING_RESEARCH_REFERENCE", "INCLUDED_IN_RESEARCH_REFERENCE_STORE"),
            _row(6, "EXCLUDED_SAMPLE_CONSTRAINED", "EXCLUDED_FROM_RESEARCH_REFERENCE_STORE"),
        ]
    )

    review = build_horizon_reference_review(candidates)

    assert review.iloc[0]["Forward_Horizon_H4_Candles"] == 3
    assert review.iloc[0]["Horizon_Reference_Utility_Class"] == "PRIMARY_REFERENCE_HORIZON"


def _row(horizon: int, tier: str, status: str) -> dict[str, object]:
    return {"Forward_Horizon_H4_Candles": horizon, "Reference_Tier": tier, "Reference_Inclusion_Status": status}
