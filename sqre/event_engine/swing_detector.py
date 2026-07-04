import pandas as pd

from sqre.event_engine.event import MarketEvent
from sqre.event_engine.event_types import EventType


class SwingDetector:
    def __init__(self, window: int = 5) -> None:
        if window < 1:
            raise ValueError("window must be >= 1")
        self.window = window

    def detect(self, data: pd.DataFrame, *, symbol: str = "", timeframe: str = "") -> list[MarketEvent]:
        events: list[MarketEvent] = []
        if len(data) < (self.window * 2) + 1:
            return events

        for index in range(self.window, len(data) - self.window):
            current = data.iloc[index]
            local = data.iloc[index - self.window : index + self.window + 1]
            high = float(current["High"])
            low = float(current["Low"])

            if high == float(local["High"].max()) and high > float(local.drop(current.name)["High"].max()):
                events.append(MarketEvent(EventType.SWING_HIGH, current["Date"].to_pydatetime(), high, symbol, timeframe, high))

            if low == float(local["Low"].min()) and low < float(local.drop(current.name)["Low"].min()):
                events.append(MarketEvent(EventType.SWING_LOW, current["Date"].to_pydatetime(), low, symbol, timeframe, low))

        return events
