import pandas as pd

from sqre.event_engine.event import MarketEvent
from sqre.event_engine.event_types import EventType


class VolatilityDetector:
    def __init__(self, *, window: int = 20, expansion_multiplier: float = 1.5, contraction_multiplier: float = 0.5) -> None:
        if window < 2:
            raise ValueError("window must be >= 2")
        self.window = window
        self.expansion_multiplier = expansion_multiplier
        self.contraction_multiplier = contraction_multiplier

    def detect(self, data: pd.DataFrame, *, symbol: str = "", timeframe: str = "") -> list[MarketEvent]:
        events: list[MarketEvent] = []
        if len(data) < self.window:
            return events

        working = data.copy()
        working["Range"] = working["High"] - working["Low"]
        working["AverageRange"] = working["Range"].rolling(self.window, min_periods=self.window).mean()

        for _, row in working.dropna(subset=["AverageRange"]).iterrows():
            range_value = float(row["Range"])
            average = float(row["AverageRange"])
            if average <= 0:
                continue

            price = float(row["Close"])
            date = row["Date"].to_pydatetime()
            metadata = {"average_range": average}

            if range_value > average * self.expansion_multiplier:
                events.append(MarketEvent(EventType.RANGE_EXPANSION, date, price, symbol, timeframe, range_value, metadata))
                events.append(MarketEvent(EventType.LARGE_CANDLE, date, price, symbol, timeframe, range_value, metadata))
            elif range_value < average * self.contraction_multiplier:
                events.append(MarketEvent(EventType.RANGE_CONTRACTION, date, price, symbol, timeframe, range_value, metadata))
                events.append(MarketEvent(EventType.SMALL_CANDLE, date, price, symbol, timeframe, range_value, metadata))

        return events
