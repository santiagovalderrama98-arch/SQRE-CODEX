"""H4 price path index for forward outcome calculations."""

from __future__ import annotations

import pandas as pd

from sqre.h4_d1_aligned_forward_outcome_research.models import PriceAnchor


class H4PricePathIndex:
    def __init__(self, h4_ohlc: pd.DataFrame) -> None:
        self.frame = h4_ohlc.reset_index(drop=True).copy()
        self._timestamp_to_index = {
            pd.Timestamp(row["Timestamp"]): index
            for index, row in self.frame.iterrows()
            if "Timestamp" in row and not pd.isna(row["Timestamp"])
        }

    def find_anchor(self, timestamp: object) -> PriceAnchor | None:
        parsed = pd.to_datetime(timestamp, errors="coerce")
        if pd.isna(parsed):
            return None
        index = self._timestamp_to_index.get(pd.Timestamp(parsed))
        if index is None:
            return None
        row = self.frame.iloc[index]
        return PriceAnchor(index=index, timestamp=pd.Timestamp(row["Timestamp"]), close=float(row["Close"]))

    def forward_window(self, anchor_index: int, horizon: int) -> pd.DataFrame:
        start = anchor_index + 1
        end = min(anchor_index + horizon, len(self.frame) - 1)
        if start > end:
            return self.frame.iloc[0:0]
        return self.frame.iloc[start : end + 1]
