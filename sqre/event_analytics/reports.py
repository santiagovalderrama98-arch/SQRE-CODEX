from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EventAnalyticsReportData:
    dataset: Path
    symbol: str
    timeframe: str
    period: str
    rows_processed: int
    total_events: int
    most_frequent_event: str
    least_frequent_event: str
    average_pivot_distance: float
    average_swing_duration: float
    most_common_sequence: str
    transition_summary: str


class EventAnalyticsReport:
    def write(self, data: EventAnalyticsReportData, output_path: Path | str) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "SQRE Event Analytics Report",
            "=" * 27,
            "",
            f"Dataset: {data.dataset}",
            f"Symbol: {data.symbol or 'UNKNOWN'}",
            f"Timeframe: {data.timeframe or 'UNKNOWN'}",
            f"Period: {data.period}",
            f"Rows processed: {data.rows_processed}",
            f"Total events: {data.total_events}",
            f"Most frequent event: {data.most_frequent_event}",
            f"Least frequent event: {data.least_frequent_event}",
            f"Average Pivot Distance: {data.average_pivot_distance:.4f} pips",
            f"Average Swing Duration: {data.average_swing_duration:.2f} seconds",
            f"Most common sequence: {data.most_common_sequence}",
            f"Transition matrix summary: {data.transition_summary}",
            "",
            "Key observations:",
            "- This report is descriptive and does not generate trading decisions.",
            "- Event frequencies and transitions should be reviewed before Market Structure work.",
            "- Sparse event types may need larger datasets before interpretation.",
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
