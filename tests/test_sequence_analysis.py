import pandas as pd

from sqre.event_analytics.sequence_analysis import SequenceAnalysis


def test_sequence_analysis_counts_configurable_sequences():
    events = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=5, freq="5min"),
            "EventType": ["PIVOT_LOW", "SWING_LOW", "RANGE_EXPANSION", "PIVOT_LOW", "SWING_LOW"],
            "Price": [1, 1, 1, 1, 1],
        }
    )

    sequences = SequenceAnalysis().analyze(events, sequence_length=3)

    assert sequences.iloc[0]["Sequence"] == "PIVOT_LOW -> SWING_LOW -> RANGE_EXPANSION"
    assert sequences.iloc[0]["Occurrences"] == 1
    assert "Percentage" in sequences.columns
