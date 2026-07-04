import pandas as pd


class DistributionAnalysis:
    def analyze(self, events: pd.DataFrame) -> pd.DataFrame:
        counts = events["EventType"].value_counts().sort_values(ascending=False)
        total = int(counts.sum())
        if total == 0:
            return pd.DataFrame(columns=["EventType", "Frequency", "RelativeFrequency", "CumulativeFrequency"])

        distribution = counts.reset_index()
        distribution.columns = ["EventType", "Frequency"]
        distribution["RelativeFrequency"] = distribution["Frequency"] / total
        distribution["CumulativeFrequency"] = distribution["RelativeFrequency"].cumsum()
        return distribution
