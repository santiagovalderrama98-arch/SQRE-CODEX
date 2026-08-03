import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.candle_alignment_mapper import build_h4_d1_alignment_map


def test_build_h4_d1_alignment_map_maps_h4_rows_by_date():
    h4 = pd.DataFrame(
        {
            "Date": ["2026-07-01 00:00:00", "2026-07-01 04:00:00"],
            "Open": [1.0, 1.1],
            "High": [1.2, 1.3],
            "Low": [0.9, 1.0],
            "Close": [1.1, 1.2],
            "Volume": [10, 11],
            "Symbol": ["EURUSD", "EURUSD"],
            "Timeframe": ["H4", "H4"],
        }
    )
    d1 = pd.DataFrame(
        {
            "Date": ["2026-07-01"],
            "D1_Period_Start": ["2026-07-01 00:00:00"],
            "D1_Period_End": ["2026-07-01 20:00:00"],
            "Open": [1.0],
            "High": [1.3],
            "Low": [0.9],
            "Close": [1.2],
            "Volume": [21],
            "H4_Candle_Count": [6],
            "D1_Candle_Quality_Class": ["FULL_H4_DERIVED_D1_CANDLE"],
        }
    )

    alignment = build_h4_d1_alignment_map(h4, d1)

    assert len(alignment) == 2
    assert set(alignment["H4_D1_Candle_Alignment_Class"]) == {"H4_D1_CANDLE_ALIGNED"}
    assert alignment["D1_Date"].tolist() == ["2026-07-01", "2026-07-01"]


def test_build_h4_d1_alignment_map_marks_missing_d1():
    h4 = pd.DataFrame(
        {
            "Date": ["2026-07-01 00:00:00"],
            "Open": [1.0],
            "High": [1.2],
            "Low": [0.9],
            "Close": [1.1],
            "Volume": [10],
            "Symbol": ["EURUSD"],
            "Timeframe": ["H4"],
        }
    )

    alignment = build_h4_d1_alignment_map(h4, pd.DataFrame())

    assert alignment.iloc[0]["H4_D1_Candle_Alignment_Class"] == "H4_D1_CANDLE_ALIGNMENT_MISSING_D1"
