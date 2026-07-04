from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from sqre.data_acquisition.loader import DataLoader
from sqre.data_acquisition.validation import DataValidator
from sqre.event_engine.event import MarketEvent
from sqre.event_engine.pivot_detector import PivotDetector
from sqre.event_engine.swing_detector import SwingDetector
from sqre.event_engine.volatility_detector import VolatilityDetector
from sqre.reports.basic_event_report import BasicEventReport


@dataclass(frozen=True)
class EventPipelineResult:
    input_path: Path
    events_path: Path
    report_path: Path
    events: int
    success: bool
    message: str


class EventPipeline:
    def __init__(self, loader=None, validator=None, detectors=None, reporter=None) -> None:
        self.loader = loader or DataLoader()
        self.validator = validator or DataValidator()
        self.detectors = detectors or [PivotDetector(), SwingDetector(), VolatilityDetector()]
        self.reporter = reporter or BasicEventReport()

    def run(self, *, input_path, output_events, output_report, symbol: str = "", timeframe: str = "") -> EventPipelineResult:
        input_path = Path(input_path)
        output_events = Path(output_events)
        output_report = Path(output_report)

        if not input_path.exists():
            return EventPipelineResult(input_path, output_events, output_report, 0, False, f"Input file not found: {input_path}")

        data = self.loader.load_csv(input_path)
        validation_summary = self.validator.validate(data)
        if not validation_summary["valid"]:
            return EventPipelineResult(
                input_path,
                output_events,
                output_report,
                0,
                False,
                f"Input validation failed: {'; '.join(validation_summary['errors'])}",
            )

        events = self._detect(data, symbol=symbol, timeframe=timeframe)
        events_frame = self._events_to_dataframe(events)
        output_events.parent.mkdir(parents=True, exist_ok=True)
        events_frame.to_csv(output_events, index=False)
        self.reporter.write(events_frame, output_report)

        return EventPipelineResult(input_path, output_events, output_report, len(events_frame), True, "Event detection completed")

    def _detect(self, data: pd.DataFrame, *, symbol: str, timeframe: str) -> list[MarketEvent]:
        events: list[MarketEvent] = []
        for detector in self.detectors:
            events.extend(detector.detect(data, symbol=symbol, timeframe=timeframe))
        return sorted(events, key=lambda event: (event.date, event.event_type.value))

    def _events_to_dataframe(self, events: list[MarketEvent]) -> pd.DataFrame:
        columns = ["Date", "EventType", "Symbol", "Timeframe", "Price", "Value"]
        if not events:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame([event.to_record() for event in events])
