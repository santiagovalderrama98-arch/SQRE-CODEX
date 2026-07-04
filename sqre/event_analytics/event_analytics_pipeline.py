from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from sqre.event_analytics.distance_analysis import DistanceAnalysis
from sqre.event_analytics.distributions import DistributionAnalysis
from sqre.event_analytics.reports import EventAnalyticsReport, EventAnalyticsReportData
from sqre.event_analytics.sequence_analysis import SequenceAnalysis
from sqre.event_analytics.session_analysis import SessionAnalysis
from sqre.event_analytics.statistics import EventStatistics
from sqre.event_analytics.transition_matrix import TransitionMatrix


@dataclass(frozen=True)
class EventAnalyticsResult:
    input_path: Path
    output_dir: Path
    rows_processed: int
    success: bool
    message: str
    outputs: dict[str, Path]


class EventAnalyticsPipeline:
    _REQUIRED_COLUMNS = {"Date", "EventType", "Price"}

    def __init__(
        self,
        statistics=None,
        distributions=None,
        distances=None,
        transitions=None,
        sequences=None,
        sessions=None,
        reporter=None,
    ) -> None:
        self.statistics = statistics or EventStatistics()
        self.distributions = distributions or DistributionAnalysis()
        self.distances = distances or DistanceAnalysis()
        self.transitions = transitions or TransitionMatrix()
        self.sequences = sequences or SequenceAnalysis()
        self.sessions = sessions or SessionAnalysis()
        self.reporter = reporter or EventAnalyticsReport()

    def run(
        self,
        *,
        input_path,
        output_dir=Path("data/reports"),
        sequence_length: int = 3,
        pip_size: float = 0.0001,
        utc_offset_hours: int = 0,
    ) -> EventAnalyticsResult:
        input_path = Path(input_path)
        output_dir = Path(output_dir)

        if not input_path.exists():
            return self._failure(input_path, output_dir, f"Input file not found: {input_path}")

        events = self._load_events(input_path)
        validation_errors = self._validate(events)
        if validation_errors:
            return self._failure(input_path, output_dir, f"Input validation failed: {'; '.join(validation_errors)}")

        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = self._output_paths(output_dir)

        frequency = self.statistics.event_frequency(events)
        time_stats = self.statistics.time_statistics(events)
        event_statistics = pd.concat([frequency, self._time_stats_as_metrics(time_stats)], ignore_index=True)
        distribution = self.distributions.analyze(events)
        transition_matrix = self.transitions.build(events)
        sequence_stats = self.sequences.analyze(events, sequence_length=sequence_length)
        distance_stats = self.distances.analyze(events, pip_size=pip_size)
        session_stats = self.sessions.analyze(events, utc_offset_hours=utc_offset_hours)

        event_statistics.to_csv(outputs["event_statistics"], index=False)
        distribution.to_csv(outputs["event_distribution"], index=False)
        transition_matrix.to_csv(outputs["transition_matrix"], index=False)
        sequence_stats.to_csv(outputs["sequence_statistics"], index=False)
        distance_stats.to_csv(outputs["distance_statistics"], index=False)
        session_stats.to_csv(outputs["session_statistics"], index=False)

        report_data = self._build_report_data(
            input_path=input_path,
            events=events,
            distribution=distribution,
            distance_stats=distance_stats,
            time_stats=time_stats,
            sequence_stats=sequence_stats,
            transition_matrix=transition_matrix,
        )
        self.reporter.write(report_data, outputs["event_analytics_report"])

        return EventAnalyticsResult(
            input_path=input_path,
            output_dir=output_dir,
            rows_processed=len(events),
            success=True,
            message="Event analytics completed",
            outputs=outputs,
        )

    def _load_events(self, input_path: Path) -> pd.DataFrame:
        events = pd.read_csv(input_path)
        if "Date" in events.columns:
            events["Date"] = pd.to_datetime(events["Date"], errors="raise")
        return events.sort_values("Date").reset_index(drop=True)

    def _validate(self, events: pd.DataFrame) -> list[str]:
        errors = []
        missing = sorted(self._REQUIRED_COLUMNS - set(events.columns))
        if missing:
            errors.append(f"Missing columns: {', '.join(missing)}")
        if events.empty:
            errors.append("Events dataset is empty")
        if not missing and not events.empty:
            if events["Date"].isna().any():
                errors.append("Date contains invalid values")
            if pd.to_numeric(events["Price"], errors="coerce").isna().any():
                errors.append("Price contains non-numeric values")
        return errors

    def _output_paths(self, output_dir: Path) -> dict[str, Path]:
        return {
            "event_statistics": output_dir / "event_statistics.csv",
            "event_distribution": output_dir / "event_distribution.csv",
            "transition_matrix": output_dir / "transition_matrix.csv",
            "sequence_statistics": output_dir / "sequence_statistics.csv",
            "distance_statistics": output_dir / "distance_statistics.csv",
            "session_statistics": output_dir / "session_statistics.csv",
            "event_analytics_report": output_dir / "event_analytics_report.txt",
        }

    def _time_stats_as_metrics(self, time_stats: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in time_stats.iterrows():
            category = row["Category"]
            rows.append({"Metric": "mean_elapsed_seconds", "Group": category, "Value": row["MeanSeconds"]})
            rows.append({"Metric": "median_elapsed_seconds", "Group": category, "Value": row["MedianSeconds"]})
            rows.append({"Metric": "std_elapsed_seconds", "Group": category, "Value": row["StdSeconds"]})
        return pd.DataFrame(rows)

    def _build_report_data(
        self,
        *,
        input_path: Path,
        events: pd.DataFrame,
        distribution: pd.DataFrame,
        distance_stats: pd.DataFrame,
        time_stats: pd.DataFrame,
        sequence_stats: pd.DataFrame,
        transition_matrix: pd.DataFrame,
    ) -> EventAnalyticsReportData:
        symbol = self._single_value(events, "Symbol")
        timeframe = self._single_value(events, "Timeframe")
        period = f"{events['Date'].min()} -> {events['Date'].max()}"
        most_frequent = distribution.iloc[0]["EventType"] if not distribution.empty else "N/A"
        least_frequent = distribution.iloc[-1]["EventType"] if not distribution.empty else "N/A"
        pivot_distance = self._average_for_pairs(distance_stats, ["Pivot Low -> Pivot High", "Pivot High -> Pivot Low"])
        swing_duration = self._time_stat(time_stats, "swings", "MeanSeconds")
        common_sequence = sequence_stats.iloc[0]["Sequence"] if not sequence_stats.empty else "N/A"
        transition_summary = self._transition_summary(transition_matrix)

        return EventAnalyticsReportData(
            dataset=input_path,
            symbol=symbol,
            timeframe=timeframe,
            period=period,
            rows_processed=len(events),
            total_events=len(events),
            most_frequent_event=str(most_frequent),
            least_frequent_event=str(least_frequent),
            average_pivot_distance=pivot_distance,
            average_swing_duration=swing_duration,
            most_common_sequence=str(common_sequence),
            transition_summary=transition_summary,
        )

    def _single_value(self, events: pd.DataFrame, column: str) -> str:
        if column not in events.columns:
            return ""
        values = [value for value in events[column].dropna().unique().tolist() if str(value)]
        return str(values[0]) if values else ""

    def _average_for_pairs(self, distance_stats: pd.DataFrame, pairs: list[str]) -> float:
        selected = distance_stats[distance_stats["Pair"].isin(pairs)]
        selected = selected[selected["Count"] > 0]
        if selected.empty:
            return 0.0
        return float(selected["Mean"].mean())

    def _time_stat(self, time_stats: pd.DataFrame, category: str, column: str) -> float:
        selected = time_stats[time_stats["Category"] == category]
        if selected.empty:
            return 0.0
        return float(selected.iloc[0][column])

    def _transition_summary(self, transition_matrix: pd.DataFrame) -> str:
        if transition_matrix.empty:
            return "No transitions available"
        row = transition_matrix.sort_values("Count", ascending=False).iloc[0]
        return f"{row['CurrentEvent']} -> {row['NextEvent']} ({int(row['Count'])} transitions)"

    def _failure(self, input_path: Path, output_dir: Path, message: str) -> EventAnalyticsResult:
        return EventAnalyticsResult(input_path, output_dir, 0, False, message, {})
