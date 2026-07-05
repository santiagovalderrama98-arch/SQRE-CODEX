"""Load detected events for Market Structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from sqre.market_structure.models import MarketEvent


class MarketStructureLoader:
    """Load and validate Phase 2 events.csv files."""

    _REQUIRED_COLUMNS = {"Date", "EventType", "Symbol", "Timeframe", "Price", "Value"}

    def load(self, path: Path | str) -> list[MarketEvent]:
        data = self.load_frame(path)
        return [self._row_to_event(row) for _, row in data.iterrows()]

    def load_frame(self, path: Path | str) -> pd.DataFrame:
        data = pd.read_csv(Path(path))
        self._validate_columns(data)
        data = data.copy()
        data["Date"] = pd.to_datetime(data["Date"], errors="raise")
        data["EventType"] = data["EventType"].astype(str).str.strip().str.upper()
        data = data.sort_values("Date").reset_index(drop=True)
        if "Event_ID" not in data.columns:
            data.insert(0, "Event_ID", [f"EVT_{index + 1:06d}" for index in range(len(data))])
        return data

    def _validate_columns(self, data: pd.DataFrame) -> None:
        missing = sorted(self._REQUIRED_COLUMNS - set(data.columns))
        if missing:
            raise ValueError(f"Missing required event columns: {', '.join(missing)}")

    def _row_to_event(self, row: pd.Series) -> MarketEvent:
        metadata = self._metadata_from_row(row)
        value = None if pd.isna(row["Value"]) or row["Value"] == "" else float(row["Value"])
        return MarketEvent(
            event_id=str(row["Event_ID"]),
            date=row["Date"].to_pydatetime(),
            event_type=str(row["EventType"]),
            symbol=str(row["Symbol"]),
            timeframe=str(row["Timeframe"]),
            price=float(row["Price"]),
            value=value,
            metadata=metadata,
        )

    def _metadata_from_row(self, row: pd.Series) -> dict[str, Any]:
        known = {"Event_ID", "Date", "EventType", "Symbol", "Timeframe", "Price", "Value"}
        return {column: row[column] for column in row.index if column not in known and not pd.isna(row[column])}
