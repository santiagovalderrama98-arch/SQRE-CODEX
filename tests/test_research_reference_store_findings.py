import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.findings import build_summary


def test_findings_produce_ready_flag_when_core_references_exist():
    candidates = pd.DataFrame(
        [
            {"Reference_Tier": "CORE_RESEARCH_REFERENCE"},
            {"Reference_Tier": "SUPPORTING_RESEARCH_REFERENCE"},
        ]
    )
    store = pd.DataFrame([{"Research_Reference_ID": "RRS_1"}])
    granularity = pd.DataFrame(
        [{"Context_Granularity": "H4_TRANSITION_ONLY", "Granularity_Reference_Utility_Class": "PRIMARY_REFERENCE_GRANULARITY"}]
    )
    horizon = pd.DataFrame(
        [{"Forward_Horizon_H4_Candles": 3, "Horizon_Reference_Utility_Class": "PRIMARY_REFERENCE_HORIZON"}]
    )

    summary = build_summary(candidates, store, pd.DataFrame(), granularity, horizon, ResearchReferenceStoreDesignConfig())

    assert summary.research_reference_store_readiness_flag == "READY_FOR_RESEARCH_REFERENCE_STORE_USAGE_REVIEW"
    assert summary.primary_reference_granularity == "H4_TRANSITION_ONLY"
    assert summary.primary_reference_horizon == "3"
