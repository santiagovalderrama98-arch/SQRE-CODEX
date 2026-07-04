import pandas as pd


class DistanceAnalysis:
    _PAIRS = {
        ("PIVOT_LOW", "PIVOT_HIGH"): "Pivot Low -> Pivot High",
        ("PIVOT_HIGH", "PIVOT_LOW"): "Pivot High -> Pivot Low",
        ("SWING_LOW", "SWING_HIGH"): "Swing Low -> Swing High",
        ("SWING_HIGH", "SWING_LOW"): "Swing High -> Swing Low",
    }

    def analyze(self, events: pd.DataFrame, pip_size: float = 0.0001) -> pd.DataFrame:
        rows = []
        for pair, label in self._PAIRS.items():
            distances = self._pair_distances(events, pair, pip_size)
            rows.append(self._stats(label, distances))
        return pd.DataFrame(rows)

    def _pair_distances(self, events: pd.DataFrame, pair, pip_size: float) -> pd.Series:
        relevant = events[events["EventType"].isin(pair)].sort_values("Date").reset_index(drop=True)
        values = []
        for index in range(len(relevant) - 1):
            current = relevant.iloc[index]
            next_event = relevant.iloc[index + 1]
            if current["EventType"] == pair[0] and next_event["EventType"] == pair[1]:
                values.append(abs(float(next_event["Price"]) - float(current["Price"])) / pip_size)
        return pd.Series(values, dtype="float64")

    def _stats(self, label: str, distances: pd.Series) -> dict:
        if distances.empty:
            return {"Pair": label, "Count": 0, "Mean": 0.0, "Median": 0.0, "Std": 0.0, "Min": 0.0, "Max": 0.0}
        return {
            "Pair": label,
            "Count": int(len(distances)),
            "Mean": float(distances.mean()),
            "Median": float(distances.median()),
            "Std": float(distances.std(ddof=0)),
            "Min": float(distances.min()),
            "Max": float(distances.max()),
        }
