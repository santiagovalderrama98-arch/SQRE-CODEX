import pandas as pd


class EventStatistics:
    def event_frequency(self, events: pd.DataFrame) -> pd.DataFrame:
        total = len(events)
        rows = [{"Metric": "total_events", "Group": "ALL", "Value": total}]

        for event_type, count in events["EventType"].value_counts().sort_index().items():
            rows.append({"Metric": "events_by_type", "Group": event_type, "Value": int(count)})

        per_day = events.groupby(events["Date"].dt.date).size()
        for day, count in per_day.items():
            rows.append({"Metric": "events_per_day", "Group": str(day), "Value": int(count)})

        per_hour = events.groupby(events["Date"].dt.hour).size()
        for hour, count in per_hour.items():
            rows.append({"Metric": "events_per_hour", "Group": f"{hour:02d}", "Value": int(count)})

        return pd.DataFrame(rows)

    def time_statistics(self, events: pd.DataFrame) -> pd.DataFrame:
        rows = []
        self._append_elapsed_stats(rows, events, "all_events")
        self._append_elapsed_stats(rows, events[events["EventType"].str.contains("SWING")], "swings")
        self._append_elapsed_stats(rows, events[events["EventType"].str.contains("PIVOT")], "pivots")
        return pd.DataFrame(rows, columns=["Category", "MeanSeconds", "MedianSeconds", "StdSeconds"])

    def _append_elapsed_stats(self, rows, events: pd.DataFrame, category: str) -> None:
        ordered = events.sort_values("Date")
        deltas = ordered["Date"].diff().dt.total_seconds().dropna()
        if deltas.empty:
            rows.append({"Category": category, "MeanSeconds": 0.0, "MedianSeconds": 0.0, "StdSeconds": 0.0})
            return
        rows.append(
            {
                "Category": category,
                "MeanSeconds": float(deltas.mean()),
                "MedianSeconds": float(deltas.median()),
                "StdSeconds": float(deltas.std(ddof=0)),
            }
        )
