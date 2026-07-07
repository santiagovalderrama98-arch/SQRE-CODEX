from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqre.event_engine.event_types import EventType


@dataclass(frozen=True)
class MarketEvent:
    event_type: EventType
    date: datetime
    price: float
    symbol: str = ""
    timeframe: str = ""
    value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        record = {
            "Date": self.date,
            "EventType": self.event_type.value,
            "Symbol": self.symbol,
            "Timeframe": self.timeframe,
            "Price": self.price,
            "Value": self.value if self.value is not None else "",
        }
        record.update({f"Meta_{key}": value for key, value in self.metadata.items()})
        return record
