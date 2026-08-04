from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_forward_outcome_inputs(base: Path) -> tuple[Path, Path, Path]:
    alignment_dir = base / "alignment"
    synchronized_dir = base / "sync"
    contextual_dir = base / "contextual"
    alignment_dir.mkdir(parents=True, exist_ok=True)
    synchronized_dir.mkdir(parents=True, exist_ok=True)
    contextual_dir.mkdir(parents=True, exist_ok=True)
    transition_alignment().to_csv(alignment_dir / "h4_transition_d1_same_time_alignment.csv", index=False)
    pd.DataFrame({"Rows": [2]}).to_csv(alignment_dir / "h4_state_d1_same_time_alignment.csv", index=False)
    pd.DataFrame({"Status": ["READY"]}).to_csv(alignment_dir / "h4_d1_same_time_alignment_summary.csv", index=False)
    h4_ohlc().to_csv(synchronized_dir / "h4_normalized_ohlc.csv", index=False)
    pd.DataFrame({"Date": ["2026-01-01"]}).to_csv(synchronized_dir / "d1_from_h4_ohlc.csv", index=False)
    pd.DataFrame({"H4_Timestamp": ["2026-01-01 00:00:00"]}).to_csv(
        synchronized_dir / "h4_d1_candle_alignment_map.csv",
        index=False,
    )
    pd.DataFrame({"Status": ["READY"]}).to_csv(synchronized_dir / "h4_d1_synchronized_data_summary.csv", index=False)
    pd.DataFrame({"Context_Profile_ID": ["CTX_1"]}).to_csv(
        contextual_dir / "h4_d1_same_time_contextual_transition_profiles.csv",
        index=False,
    )
    pd.DataFrame({"Context_Profile_ID": ["CTX_1"]}).to_csv(
        contextual_dir / "h4_d1_context_sample_adequacy_review.csv",
        index=False,
    )
    pd.DataFrame({"Context_Profile_Count": [1]}).to_csv(
        contextual_dir / "h4_d1_same_time_contextual_transition_review_summary.csv",
        index=False,
    )
    return alignment_dir, synchronized_dir, contextual_dir


def transition_alignment() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "H4_D1_Transition_Alignment_ID": "ALIGN_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_ID": "H4_TRN_1",
                "H4_Transition_Time": "2026-01-01 04:00:00",
                "H4_Transition_Label": "A -> B",
                "H4_Source_State": "A",
                "H4_Target_State": "B",
                "D1_State_ID": "D1_1",
                "D1_Date": "2026-01-01",
                "D1_Market_State": "D1_TREND",
                "D1_Regime_Label": "D1_EXPANSION",
                "D1_Structure_Direction": "UP",
            },
            {
                "H4_D1_Transition_Alignment_ID": "ALIGN_2",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "H4_Transition_ID": "H4_TRN_2",
                "H4_Transition_Time": "2026-01-01 20:00:00",
                "H4_Transition_Label": "B -> C",
                "H4_Source_State": "B",
                "H4_Target_State": "C",
                "D1_State_ID": "D1_1",
                "D1_Date": "2026-01-01",
                "D1_Market_State": "D1_RANGE",
                "D1_Regime_Label": "D1_ROTATION",
                "D1_Structure_Direction": "DOWN",
            },
        ]
    )


def h4_ohlc() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _bar("2026-01-01 00:00:00", 1.0990, 1.1010, 1.0980, 1.0995),
            _bar("2026-01-01 04:00:00", 1.0995, 1.1010, 1.0985, 1.1000),
            _bar("2026-01-01 08:00:00", 1.1000, 1.1020, 1.0990, 1.1010),
            _bar("2026-01-01 12:00:00", 1.1010, 1.1030, 1.1005, 1.1020),
            _bar("2026-01-01 16:00:00", 1.1020, 1.1025, 1.0980, 1.0990),
            _bar("2026-01-01 20:00:00", 1.0990, 1.1000, 1.0970, 1.0980),
            _bar("2026-01-02 00:00:00", 1.0980, 1.0990, 1.0960, 1.0970),
        ]
    )


def _bar(date: str, open_: float, high: float, low: float, close: float) -> dict[str, object]:
    return {
        "Date": date,
        "Open": open_,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": 0,
    }
