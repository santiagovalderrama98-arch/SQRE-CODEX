from __future__ import annotations

import pandas as pd
import pytest

from sqre.market_structure.loader import MarketStructureLoader


def test_market_structure_loader_sorts_events_and_adds_ids(tmp_path) -> None:
    path = tmp_path / "events.csv"
    pd.DataFrame(
        {
            "Date": ["2026-01-01 00:05:00", "2026-01-01 00:00:00"],
            "EventType": ["pivot_high", "PIVOT_LOW"],
            "Symbol": ["EURUSD", "EURUSD"],
            "Timeframe": ["M5", "M5"],
            "Price": [1.1010, 1.1000],
            "Value": [1.1010, 1.1000],
            "Detector": ["test", "test"],
        }
    ).to_csv(path, index=False)

    events = MarketStructureLoader().load(path)

    assert [event.event_id for event in events] == ["EVT_000001", "EVT_000002"]
    assert [event.event_type for event in events] == ["PIVOT_LOW", "PIVOT_HIGH"]
    assert events[0].metadata["Detector"] == "test"


def test_market_structure_loader_rejects_missing_columns(tmp_path) -> None:
    path = tmp_path / "events.csv"
    pd.DataFrame({"Date": ["2026-01-01"], "EventType": ["PIVOT_LOW"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Missing required event columns"):
        MarketStructureLoader().load(path)
