from __future__ import annotations

from pathlib import Path

from sqre.price_outcome_research.models import PriceOutcomeResearchSummary
from sqre.price_outcome_research.reports import write_price_outcome_research_report


FORBIDDEN_REPORT_TERMS = [
    "Buy",
    "Sell",
    "Entry",
    "Exit",
    "Take profit",
    "Stop loss",
    "Trade signal",
    "Trade setup",
    "Reversal expected",
    "Continuation expected",
    "Opportunity",
    "Profitable",
    "Recommendation",
    "Edge",
]


def test_price_outcome_report_contains_summary_and_avoids_forbidden_language(tmp_path) -> None:
    report_path = tmp_path / "price_outcome_research_report.txt"
    summary = PriceOutcomeResearchSummary(
        symbol="EURUSD",
        timeframe="H1",
        period_start=None,
        period_end=None,
        conditions_evaluated=6,
        condition_types=["STATE_CONDITION", "TRANSITION_CONDITION"],
        price_outcomes_generated=12,
        forward_windows=[3, 6, 12],
        pip_size=0.0001,
        minimum_sample_size=5,
        summary_rows=8,
        distribution_rows=9,
        low_sample_conditions=4,
        average_forward_close_return_pips=2.5,
        median_forward_close_return_pips=1.0,
        average_forward_range_pips=20.0,
        average_favorable_displacement_pips=12.0,
        average_adverse_displacement_pips=8.0,
        average_outcome_magnitude_pips=5.0,
        direction_alignment_rate=0.5,
        most_observed_condition="A",
        largest_average_forward_range_condition="B",
        highest_direction_alignment_condition="A -> B",
        price_outcomes_path=Path("data/research/price_outcomes.csv"),
        condition_price_outcome_summary_path=Path("data/research/condition_price_outcome_summary.csv"),
        price_outcome_distributions_path=Path("data/research/price_outcome_distributions.csv"),
        report_path=report_path,
    )

    write_price_outcome_research_report(report_path, summary, [], [], [])
    text = report_path.read_text(encoding="utf-8")

    assert "Conditions Evaluated: 6" in text
    assert "Low Sample Conditions: 4" in text
    assert "Price outcomes: data/research/price_outcomes.csv" in text
    for term in FORBIDDEN_REPORT_TERMS:
        assert term not in text
