import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.d1_aggregator import build_d1_from_h4


def _h4_frame(dates: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": list(range(1, len(dates) + 1)),
            "High": [value + 0.5 for value in range(1, len(dates) + 1)],
            "Low": [value - 0.5 for value in range(1, len(dates) + 1)],
            "Close": [value + 0.25 for value in range(1, len(dates) + 1)],
            "Volume": [10] * len(dates),
            "Symbol": ["EURUSD"] * len(dates),
            "Timeframe": ["H4"] * len(dates),
        }
    )


def test_build_d1_from_h4_aggregates_ohlcv():
    frame = _h4_frame(
        [
            "2026-07-01 00:00:00",
            "2026-07-01 04:00:00",
            "2026-07-01 08:00:00",
            "2026-07-01 12:00:00",
            "2026-07-01 16:00:00",
            "2026-07-01 20:00:00",
        ]
    )

    d1 = build_d1_from_h4(frame, H4D1SynchronizedDataPreparationConfig())

    assert len(d1) == 1
    row = d1.iloc[0]
    assert row["Open"] == 1
    assert row["High"] == 6.5
    assert row["Low"] == 0.5
    assert row["Close"] == 6.25
    assert row["Volume"] == 60
    assert row["D1_Candle_Quality_Class"] == "FULL_H4_DERIVED_D1_CANDLE"


def test_build_d1_from_h4_classifies_partial_daily_coverage():
    frame = _h4_frame(
        [
            "2026-07-01 00:00:00",
            "2026-07-01 04:00:00",
            "2026-07-01 08:00:00",
            "2026-07-01 12:00:00",
        ]
    )

    d1 = build_d1_from_h4(frame, H4D1SynchronizedDataPreparationConfig())

    assert d1.iloc[0]["D1_Candle_Quality_Class"] == "PARTIAL_H4_DERIVED_D1_CANDLE"
