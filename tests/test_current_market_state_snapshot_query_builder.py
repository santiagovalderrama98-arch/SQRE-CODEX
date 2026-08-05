import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.snapshot_query_builder import build_snapshot_query_requests


def test_query_builder_creates_one_query_for_requested_horizon():
    context = _context()
    config = CurrentMarketStateSnapshotResearchConfig(snapshot_forward_horizon=1)

    queries = build_snapshot_query_requests(context, config)

    assert len(queries) == 1
    assert queries.iloc[0]["Requested_Forward_Horizon_H4_Candles"] == 1


def test_query_builder_creates_preferred_horizon_queries():
    context = _context()
    config = CurrentMarketStateSnapshotResearchConfig(preferred_horizons=[1, 2, 3])

    queries = build_snapshot_query_requests(context, config)

    assert list(queries["Requested_Forward_Horizon_H4_Candles"]) == [1, 2, 3]


def _context() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Snapshot_ID": "CMS_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "Snapshot_Source": "USER_SUPPLIED_CONTEXT",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Snapshot_Validation_Status": "VALID_SNAPSHOT_CONTEXT",
            }
        ]
    )
