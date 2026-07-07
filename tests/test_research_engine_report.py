from __future__ import annotations

from pathlib import Path

from sqre.research_engine.models import ResearchEngineSummary
from sqre.research_engine.reports import write_research_engine_report


def test_research_engine_report_uses_descriptive_language(tmp_path) -> None:
    report_path = tmp_path / "research_engine_report.txt"
    summary = ResearchEngineSummary(
        symbol="EURUSD",
        timeframe="M5",
        period_start=None,
        period_end=None,
        states_processed=6,
        transitions_processed=5,
        conditions_evaluated=10,
        forward_windows=[1, 2],
        minimum_sample_size=5,
        forward_state_rows=3,
        forward_transition_rows=2,
        preceding_state_rows=1,
        sequence_outcome_rows=1,
        condition_summary_rows=10,
        low_sample_conditions=4,
        most_common_forward_state_result="A",
        most_common_preceding_state_result="B",
        most_common_sequence_outcome="C",
        forward_state_distributions_path=Path("data/research/forward_state_distributions.csv"),
        forward_transition_distributions_path=Path("data/research/forward_transition_distributions.csv"),
        preceding_state_distributions_path=Path("data/research/preceding_state_distributions.csv"),
        sequence_outcomes_path=Path("data/research/sequence_outcomes.csv"),
        condition_summaries_path=Path("data/research/condition_summaries.csv"),
        report_path=report_path,
    )

    write_research_engine_report(report_path, summary)
    text = report_path.read_text(encoding="utf-8")

    assert "States Processed: 6" in text
    assert "Conditions Evaluated: 10" in text
    assert "observed historical occurrence" in text
    assert "Buy" not in text
    assert "Sell" not in text
    assert "Trade signal" not in text
