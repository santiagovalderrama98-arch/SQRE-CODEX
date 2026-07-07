"""Research Engine report writer."""

from __future__ import annotations

from pathlib import Path

from sqre.research_engine.models import ResearchEngineSummary


def write_research_engine_report(path: Path | str, summary: ResearchEngineSummary) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(summary), encoding="utf-8")


def _build_report(summary: ResearchEngineSummary) -> str:
    lines = [
        "SQRE Research Engine Report",
        "===========================",
        "",
        f"Symbol: {summary.symbol}",
        f"Timeframe: {summary.timeframe}",
        f"Period: {_period(summary)}",
        f"States Processed: {summary.states_processed}",
        f"Transitions Processed: {summary.transitions_processed}",
        f"Conditions Evaluated: {summary.conditions_evaluated}",
        f"Forward Windows: {_forward_windows(summary.forward_windows)}",
        f"Minimum Sample Size: {summary.minimum_sample_size}",
        "",
        f"Forward State Rows: {summary.forward_state_rows}",
        f"Forward Transition Rows: {summary.forward_transition_rows}",
        f"Preceding State Rows: {summary.preceding_state_rows}",
        f"Sequence Outcome Rows: {summary.sequence_outcome_rows}",
        f"Condition Summary Rows: {summary.condition_summary_rows}",
        f"Low Sample Conditions: {summary.low_sample_conditions}",
        "",
        f"Most Common Forward State Result: {summary.most_common_forward_state_result}",
        f"Most Common Preceding State Result: {summary.most_common_preceding_state_result}",
        f"Most Common Sequence Outcome: {summary.most_common_sequence_outcome}",
        "",
        "Output Files:",
        f"- Forward state distributions: {summary.forward_state_distributions_path}",
        f"- Forward transition distributions: {summary.forward_transition_distributions_path}",
        f"- Preceding state distributions: {summary.preceding_state_distributions_path}",
        f"- Sequence outcomes: {summary.sequence_outcomes_path}",
        f"- Condition summaries: {summary.condition_summaries_path}",
        "",
        "Key Observations:",
        "- This report is descriptive and uses only the processed dataset.",
        "- Frequencies describe observed historical occurrence inside this dataset.",
        "- Low sample size conditions should be reviewed before interpretation.",
        "- No trading signals, price outcome research, or operational guidance is generated.",
        "",
    ]
    return "\n".join(lines)


def _period(summary: ResearchEngineSummary) -> str:
    if summary.period_start is None or summary.period_end is None:
        return "UNKNOWN"
    return f"{summary.period_start} -> {summary.period_end}"


def _forward_windows(forward_windows: list[int]) -> str:
    if not forward_windows:
        return "NONE"
    return ", ".join(str(window) for window in forward_windows)
