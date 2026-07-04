import pandas as pd


class SessionAnalysis:
    def analyze(self, events: pd.DataFrame, utc_offset_hours: int = 0) -> pd.DataFrame:
        working = events.copy()
        adjusted = working["Date"] + pd.to_timedelta(utc_offset_hours, unit="h")
        working["Session"] = adjusted.dt.hour.map(self._session_for_hour)

        grouped = working.groupby(["Session", "EventType"]).size().reset_index(name="Count")
        totals = grouped.groupby("Session")["Count"].transform("sum")
        grouped["RelativeFrequency"] = grouped["Count"] / totals
        return grouped.sort_values(["Session", "Count"], ascending=[True, False]).reset_index(drop=True)

    def _session_for_hour(self, hour: int) -> str:
        if 0 <= hour < 7:
            return "Asian"
        if 7 <= hour < 13:
            return "London"
        if 13 <= hour < 21:
            return "NewYork"
        return "Other"
