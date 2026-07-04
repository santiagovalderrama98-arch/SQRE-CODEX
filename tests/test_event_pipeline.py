import pandas as pd

from sqre.event_engine.event_pipeline import EventPipeline


def test_event_pipeline_writes_events_and_report(tmp_path):
    input_path = tmp_path / "EURUSD_M5.csv"
    output_events = tmp_path / "events.csv"
    output_report = tmp_path / "event_report.txt"

    data = pd.DataFrame(
        {
            "Date": pd.date_range("2026-01-01", periods=30, freq="5min"),
            "Open": [1.0] * 30,
            "High": [1.01] * 30,
            "Low": [0.99] * 30,
            "Close": [1.0] * 30,
            "Volume": [0] * 30,
        }
    )
    data.loc[5, "High"] = 1.5
    data.loc[10, "Low"] = 0.5
    data.to_csv(input_path, index=False)

    result = EventPipeline().run(
        input_path=input_path,
        output_events=output_events,
        output_report=output_report,
        symbol="EURUSD",
        timeframe="M5",
    )

    assert result.success
    assert output_events.exists()
    assert output_report.exists()

    events = pd.read_csv(output_events)
    assert not events.empty
    assert {"Date", "EventType", "Symbol", "Timeframe", "Price", "Value"}.issubset(events.columns)
    assert set(events["Symbol"]) == {"EURUSD"}
    assert "Total events:" in output_report.read_text(encoding="utf-8")


def test_event_pipeline_fails_on_invalid_input(tmp_path):
    input_path = tmp_path / "bad.csv"
    output_events = tmp_path / "events.csv"
    output_report = tmp_path / "event_report.txt"

    pd.DataFrame({"Date": ["2026-01-01"], "Open": [1.0]}).to_csv(input_path, index=False)

    result = EventPipeline().run(
        input_path=input_path,
        output_events=output_events,
        output_report=output_report,
    )

    assert not result.success
    assert not output_events.exists()
    assert "validation failed" in result.message.lower()


def test_event_pipeline_fails_when_input_file_is_missing(tmp_path):
    result = EventPipeline().run(
        input_path=tmp_path / "missing.csv",
        output_events=tmp_path / "events.csv",
        output_report=tmp_path / "event_report.txt",
    )

    assert not result.success
    assert "not found" in result.message.lower()
