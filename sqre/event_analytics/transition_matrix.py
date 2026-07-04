import pandas as pd


class TransitionMatrix:
    def build(self, events: pd.DataFrame) -> pd.DataFrame:
        ordered = events.sort_values("Date").reset_index(drop=True)
        if len(ordered) < 2:
            return pd.DataFrame(columns=["CurrentEvent", "NextEvent", "Count", "Probability", "Percentage"])

        transitions = pd.DataFrame(
            {
                "CurrentEvent": ordered["EventType"].iloc[:-1].to_numpy(),
                "NextEvent": ordered["EventType"].iloc[1:].to_numpy(),
            }
        )
        counts = transitions.groupby(["CurrentEvent", "NextEvent"]).size().reset_index(name="Count")
        totals = counts.groupby("CurrentEvent")["Count"].transform("sum")
        counts["Probability"] = counts["Count"] / totals
        counts["Percentage"] = counts["Probability"] * 100
        return counts.sort_values(["CurrentEvent", "Count", "NextEvent"], ascending=[True, False, True]).reset_index(drop=True)
