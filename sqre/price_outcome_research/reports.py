"""Price Outcome Research report writer."""

from __future__ import annotations

from pathlib import Path

from sqre.price_outcome_research.models import (
    ConditionPriceOutcomeSummaryRow,
    PriceOutcomeDistributionRow,
    PriceOutcomeResearchSummary,
    PriceOutcomeRow,
)


def write_price_outcome_research_report(
    path: Path | str,
    summary: PriceOutcomeResearchSummary,
    outcome_rows: list[PriceOutcomeRow],
    summary_rows: list[ConditionPriceOutcomeSummaryRow],
    distribution_rows: list[PriceOutcomeDistributionRow],
) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _build_report(summary, outcome_rows, summary_rows, distribution_rows),
        encoding="utf-8",
    )


def _build_report(
    summary: PriceOutcomeResearchSummary,
    outcome_rows: list[PriceOutcomeRow],
    summary_rows: list[ConditionPriceOutcomeSummaryRow],
    distribution_rows: list[PriceOutcomeDistributionRow],
) -> str:
    lines = [
        "SQRE Price Outcome Research Report",
        "==================================",
        "",
        f"Symbol: {summary.symbol}",
        f"Timeframe: {summary.timeframe}",
        f"Period: {_period(summary)}",
        f"Conditions Evaluated: {summary.conditions_evaluated}",
        f"Condition Types: {', '.join(summary.condition_types) if summary.condition_types else 'NONE'}",
        f"Price Outcomes Generated: {summary.price_outcomes_generated}",
        f"Forward Windows: {', '.join(str(window) for window in summary.forward_windows)}",
        f"Pip Size: {summary.pip_size}",
        f"Minimum Sample Size: {summary.minimum_sample_size}",
        "",
        "Outcome Summary:",
        f"- Summary Rows: {summary.summary_rows}",
        f"- Distribution Rows: {summary.distribution_rows}",
        f"- Low Sample Conditions: {summary.low_sample_conditions}",
        "",
        "Aggregate Price Outcomes:",
        f"- Average Forward Close Return Pips: {summary.average_forward_close_return_pips:.4f}",
        f"- Median Forward Close Return Pips: {summary.median_forward_close_return_pips:.4f}",
        f"- Average Forward Range Pips: {summary.average_forward_range_pips:.4f}",
        f"- Average Favorable Displacement Pips: {summary.average_favorable_displacement_pips:.4f}",
        f"- Average Adverse Displacement Pips: {summary.average_adverse_displacement_pips:.4f}",
        f"- Average Outcome Magnitude Pips: {summary.average_outcome_magnitude_pips:.4f}",
        f"- Direction Alignment Rate: {summary.direction_alignment_rate:.4f}",
        "",
        f"Most Observed Condition: {summary.most_observed_condition}",
        f"Largest Average Forward Range Condition: {summary.largest_average_forward_range_condition}",
        f"Highest Direction Alignment Condition: {summary.highest_direction_alignment_condition}",
        "",
        "Output Files:",
        f"- Price outcomes: {summary.price_outcomes_path}",
        f"- Condition price outcome summary: {summary.condition_price_outcome_summary_path}",
        f"- Price outcome distributions: {summary.price_outcome_distributions_path}",
        "",
        "Key Observations:",
        "- This report is descriptive and summarizes observed forward price outcomes.",
        "- Price outcomes are calculated only from the processed dataset.",
        "- Low sample size conditions are marked explicitly.",
        "- No operational decision guidance is generated.",
        "",
    ]
    return "\n".join(lines)


def _period(summary: PriceOutcomeResearchSummary) -> str:
    if summary.period_start is None or summary.period_end is None:
        return "UNKNOWN"
    return f"{summary.period_start} -> {summary.period_end}"
