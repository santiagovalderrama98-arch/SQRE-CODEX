import pandas as pd

from sqre.event_analytics.distance_analysis import DistanceAnalysis


def test_distance_analysis_computes_pip_distance_between_pairs():
    events = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=2, freq="5min"),
            "EventType": ["PIVOT_LOW", "PIVOT_HIGH"],
            "Price": [1.1000, 1.1050],
        }
    )

    distances = DistanceAnalysis().analyze(events, pip_size=0.0001)
    row = distances[distances["Pair"] == "Pivot Low -> Pivot High"].iloc[0]

    assert row["Count"] == 1
    assert round(row["Mean"], 4) == 50.0
