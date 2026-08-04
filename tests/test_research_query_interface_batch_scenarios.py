import pandas as pd

from sqre.research_query_interface_design.batch_query_scenario_builder import build_batch_query_source_rows
from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig


def test_batch_scenarios_expand_alignment_horizons():
    config = ResearchQueryInterfaceDesignConfig(preferred_horizons=[1, 2])
    alignment = pd.DataFrame(
        [{"H4_Transition_Label": "A_TO_B", "D1_Market_State": "STATE", "D1_Regime_Label": "REGIME", "D1_Structure_Direction": "UP"}]
    )

    rows = build_batch_query_source_rows(pd.DataFrame(), alignment, pd.DataFrame(), config)

    assert [row["Requested_Forward_Horizon_H4_Candles"] for row in rows] == [1, 2]
    assert rows[0]["Query_Source"] == "HISTORICAL_ALIGNMENT_BATCH_QUERY"

