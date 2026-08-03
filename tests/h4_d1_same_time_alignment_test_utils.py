from pathlib import Path

import pandas as pd


def write_same_time_alignment_fixture(base: Path) -> tuple[Path, Path]:
    timestamped_dir = base / "timestamped"
    synchronized_dir = base / "sync"
    timestamped_dir.mkdir(parents=True, exist_ok=True)
    synchronized_dir.mkdir(parents=True, exist_ok=True)
    h4_states().to_csv(timestamped_dir / "timestamped_h4_market_states.csv", index=False)
    h4_transitions().to_csv(timestamped_dir / "timestamped_h4_state_transitions.csv", index=False)
    d1_states().to_csv(timestamped_dir / "timestamped_d1_market_states.csv", index=False)
    pd.DataFrame({"Status": ["READY_FOR_H4_D1_SAME_TIME_ALIGNMENT_TABLE"]}).to_csv(
        timestamped_dir / "timestamped_h4_d1_state_regime_summary.csv",
        index=False,
    )
    candle_map().to_csv(synchronized_dir / "h4_d1_candle_alignment_map.csv", index=False)
    return timestamped_dir, synchronized_dir


def h4_states() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "H4_State_ID": ["H4_STATE_000001", "H4_STATE_000002", "H4_STATE_000003"],
            "Symbol": ["EURUSD", "EURUSD", "EURUSD"],
            "Timeframe": ["H4", "H4", "H4"],
            "State_Event_Time": ["2026-07-01 04:00:00", "2026-07-01 12:00:00", "2026-07-02 04:00:00"],
            "State_Event_Date": ["2026-07-01", "2026-07-01", "2026-07-02"],
            "Market_State": ["DIRECTIONAL_EXPANSION", "COMPLEX_CONSOLIDATION", "DIRECTIONAL_DRIFT"],
        }
    )


def h4_transitions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "H4_Transition_ID": ["H4_TRN_000001", "H4_TRN_000002"],
            "Symbol": ["EURUSD", "EURUSD"],
            "Timeframe": ["H4", "H4"],
            "Transition_Time": ["2026-07-01 12:00:00", "2026-07-02 04:00:00"],
            "Transition_Date": ["2026-07-01", "2026-07-02"],
            "Source_State": ["DIRECTIONAL_EXPANSION", "COMPLEX_CONSOLIDATION"],
            "Target_State": ["COMPLEX_CONSOLIDATION", "DIRECTIONAL_DRIFT"],
            "Transition_Label": [
                "DIRECTIONAL_EXPANSION -> COMPLEX_CONSOLIDATION",
                "COMPLEX_CONSOLIDATION -> DIRECTIONAL_DRIFT",
            ],
        }
    )


def d1_states() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "D1_State_ID": ["D1_STATE_000001", "D1_STATE_000002"],
            "Symbol": ["EURUSD", "EURUSD"],
            "Timeframe": ["D1", "D1"],
            "D1_Date": ["2026-07-01", "2026-07-02"],
            "D1_Period_Start": ["2026-07-01 00:00:00", "2026-07-02 00:00:00"],
            "D1_Period_End": ["2026-07-01 23:59:59", "2026-07-02 23:59:59"],
            "Market_State": ["D1_DIRECTIONAL_EXPANSION", "D1_COMPLEX_CONSOLIDATION"],
            "Regime_Label": ["D1_DIRECTIONAL_REGIME", "D1_CONSOLIDATION_REGIME"],
            "Structure_Direction": ["UP", "NEUTRAL"],
        }
    )


def candle_map() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "H4_Timestamp": ["2026-07-03 04:00:00"],
            "H4_Date": ["2026-07-03"],
            "D1_Date": ["2026-07-02"],
        }
    )
