import pandas as pd


class SequenceAnalysis:
    def analyze(self, events: pd.DataFrame, sequence_length: int = 3) -> pd.DataFrame:
        if sequence_length < 2:
            raise ValueError("sequence_length must be >= 2")

        ordered = events.sort_values("Date").reset_index(drop=True)
        if len(ordered) < sequence_length:
            return pd.DataFrame(columns=["Sequence", "Occurrences", "Frequency", "Percentage"])

        event_types = ordered["EventType"].tolist()
        sequences = [
            " -> ".join(event_types[index : index + sequence_length])
            for index in range(0, len(event_types) - sequence_length + 1)
        ]

        counts = pd.Series(sequences).value_counts().reset_index()
        counts.columns = ["Sequence", "Occurrences"]
        total = int(counts["Occurrences"].sum())
        counts["Frequency"] = counts["Occurrences"] / total
        counts["Percentage"] = counts["Frequency"] * 100
        return counts
