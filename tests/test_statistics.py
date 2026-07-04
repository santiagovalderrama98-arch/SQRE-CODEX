import pandas as pd

from sqre.event_analytics.event_analytics_pipeline import EventAnalyticsPipeline
from sqre.event_analytics.statistics import EventStatistics


def sample_events():
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2026-07-01 00:00:00",
                    "2026-07-01 01:00:00",
                    "2026-07-01 08:00:00",
                    "2026-07-01 14:00:00",
                ]
            ),
            "EventType": ["PIVOT_LOW", "PIVOT_HIGH", "SWING_LOW", "SWING_HIGH"],
            "Symbol": ["EURUSD"] * 4,
            "Timeframe": ["M5"] * 4,
            "Price": [1.1000, 1.1050, 1.1010, 1.1100],
            "Value": [1.1000, 1.1050, 1.1010, 1.1100],
        }
    )


def test_event_frequency_computes_totals_by_type_day_and_hour():
    stats = EventStatistics().event_frequency(sample_events())

    assert stats[(stats["Metric"] == "total_events")]["Value"].iloc[0] == 4
    assert "PIVOT_HIGH" in stats["Group"].tolist()
    assert "2026-07-01" in stats["Group"].tolist()
    assert "14" in stats["Group"].tolist()


def test_event_analytics_pipeline_writes_all_outputs(tmp_path):
    input_path = tmp_path / "events.csv"
    output_dir = tmp_path / "reports"
    sample_events().to_csv(input_path, index=False)

    result = EventAnalyticsPipeline().run(input_path=input_path, output_dir=output_dir)

    assert result.success
    assert result.rows_processed == 4
    expected = {
        "event_statistics",
        "event_distribution",
        "transition_matrix",
        "sequence_statistics",
        "distance_statistics",
        "session_statistics",
        "event_analytics_report",
    }
    assert set(result.outputs) == expected
    assert all(path.exists() for path in result.outputs.values())


def test_event_analytics_pipeline_validates_required_columns(tmp_path):
    input_path = tmp_path / "bad_events.csv"
    pd.DataFrame({"Date": ["2026-07-01"], "EventType": ["PIVOT_HIGH"]}).to_csv(input_path, index=False)

    result = EventAnalyticsPipeline().run(input_path=input_path, output_dir=tmp_path / "reports")

    assert not result.success
    assert "missing columns" in result.message.lower()
