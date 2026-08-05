import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.snapshot_context_builder import build_snapshot_context


def test_latest_context_prefers_same_time_alignment_latest_row():
    frames = {
        "transition_alignment": pd.DataFrame(
            [
                {
                    "H4_Transition_Timestamp": "2026-01-01T00:00:00Z",
                    "H4_Transition_Label": "OLD",
                    "D1_Market_State": "STATE_A",
                    "D1_Regime_Label": "REGIME_A",
                },
                {
                    "H4_Transition_Timestamp": "2026-01-02T00:00:00Z",
                    "H4_Transition_Label": "NEW",
                    "D1_Market_State": "STATE_B",
                    "D1_Regime_Label": "REGIME_B",
                    "D1_Structure_Direction": "UP",
                },
            ]
        )
    }

    context = build_snapshot_context(frames, CurrentMarketStateSnapshotResearchConfig())

    row = context.iloc[0]
    assert row["Snapshot_Source"] == "SAME_TIME_ALIGNMENT_LATEST_ROW"
    assert row["H4_Transition_Label"] == "NEW"
    assert row["Snapshot_Timestamp_Status"] == "TIMESTAMP_AVAILABLE"


def test_latest_context_falls_back_to_usage_scenarios():
    frames = {
        "transition_alignment": pd.DataFrame(),
        "h4_timestamped_transitions": pd.DataFrame(),
        "usage_scenarios": pd.DataFrame(
            [{"H4_Transition_Label": "FALLBACK", "D1_Market_State": "STATE", "D1_Regime_Label": "REGIME"}]
        ),
    }

    context = build_snapshot_context(frames, CurrentMarketStateSnapshotResearchConfig())

    assert context.iloc[0]["Snapshot_Source"] == "REFERENCE_USAGE_SCENARIO_LATEST_ROW"
    assert context.iloc[0]["Snapshot_Mode"] == "FALLBACK_REFERENCE_USAGE_SNAPSHOT"


def test_user_supplied_context_is_supported():
    config = CurrentMarketStateSnapshotResearchConfig(
        snapshot_mode="USER_SUPPLIED_SNAPSHOT",
        snapshot_h4_transition_label="USER_TRANSITION",
        snapshot_d1_market_state="STATE",
        snapshot_d1_regime_label="REGIME",
        snapshot_timestamp="2026-08-04T00:00:00Z",
    )

    context = build_snapshot_context({}, config)

    assert context.iloc[0]["Snapshot_Source"] == "USER_SUPPLIED_CONTEXT"
    assert context.iloc[0]["Snapshot_Timestamp_Status"] == "USER_SUPPLIED_TIMESTAMP"
    assert context.iloc[0]["Snapshot_Validation_Status"] == "VALID_SNAPSHOT_CONTEXT"
