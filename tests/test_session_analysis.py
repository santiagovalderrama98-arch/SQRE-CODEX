import pandas as pd

from sqre.event_analytics.session_analysis import SessionAnalysis


def test_session_analysis_groups_events_by_utc_session():
    events = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2026-01-01 01:00:00", "2026-01-01 08:00:00", "2026-01-01 14:00:00"]),
            "EventType": ["PIVOT_LOW", "PIVOT_HIGH", "SWING_HIGH"],
            "Price": [1.0, 1.1, 1.2],
        }
    )

    sessions = SessionAnalysis().analyze(events)

    assert {"Asian", "London", "NewYork"}.issubset(set(sessions["Session"]))
    assert sessions["Count"].sum() == 3
