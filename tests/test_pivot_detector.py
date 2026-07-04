import pandas as pd

from sqre.event_engine.event_types import EventType
from sqre.event_engine.pivot_detector import PivotDetector


def test_pivot_detector_finds_pivot_high_and_low():
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=7, freq="5min"),
            "Open": [1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 1.0],
            "High": [1.1, 1.2, 1.5, 1.2, 1.1, 1.0, 1.1],
            "Low": [0.9, 1.0, 1.1, 1.0, 0.8, 0.7, 0.9],
            "Close": [1.05, 1.15, 1.25, 1.05, 0.95, 0.95, 1.05],
            "Volume": [0, 0, 0, 0, 0, 0, 0],
        }
    )

    events = PivotDetector(window=1).detect(data, symbol="EURUSD", timeframe="M5")
    event_types = [event.event_type for event in events]

    assert EventType.PIVOT_HIGH in event_types
    assert EventType.PIVOT_LOW in event_types
    assert all(event.symbol == "EURUSD" for event in events)
    assert all(event.timeframe == "M5" for event in events)
