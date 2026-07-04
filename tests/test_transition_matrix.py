import pandas as pd

from sqre.event_analytics.transition_matrix import TransitionMatrix


def test_transition_matrix_computes_counts_and_probabilities():
    events = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=4, freq="5min"),
            "EventType": ["PIVOT_LOW", "PIVOT_HIGH", "PIVOT_LOW", "PIVOT_HIGH"],
            "Price": [1.0, 1.1, 1.0, 1.2],
        }
    )

    matrix = TransitionMatrix().build(events)

    row = matrix[(matrix["CurrentEvent"] == "PIVOT_LOW") & (matrix["NextEvent"] == "PIVOT_HIGH")].iloc[0]
    assert row["Count"] == 2
    assert row["Probability"] == 1.0
    assert row["Percentage"] == 100.0
