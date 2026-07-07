from __future__ import annotations

import pandas as pd

from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.price_outcome_pipeline import run_price_outcome_research
from tests.price_outcome_test_utils import write_price_outcome_inputs
from tests.test_price_outcome_report import FORBIDDEN_REPORT_TERMS


def test_price_outcome_pipeline_writes_outputs_and_summary(tmp_path) -> None:
    states_path, transitions_path, ohlc_path = write_price_outcome_inputs(tmp_path)
    output_dir = tmp_path / "research"
    report_path = tmp_path / "reports" / "price_outcome_research_report.txt"

    summary = run_price_outcome_research(
        states_path=states_path,
        transitions_path=transitions_path,
        ohlc_path=ohlc_path,
        output_dir=output_dir,
        report_path=report_path,
        config=PriceOutcomeResearchConfig(forward_candles=[1, 2], minimum_sample_size=2),
    )

    assert summary.conditions_evaluated == 6
    assert summary.price_outcomes_generated > 0
    assert summary.summary_rows > 0
    assert summary.distribution_rows > 0

    price_outcomes = pd.read_csv(output_dir / "price_outcomes.csv")
    summaries = pd.read_csv(output_dir / "condition_price_outcome_summary.csv")
    distributions = pd.read_csv(output_dir / "price_outcome_distributions.csv")

    assert {
        "Outcome_ID",
        "Condition_ID",
        "Reference_Time",
        "Forward_Close_Return_Pips",
        "Complete_Forward_Window",
    }.issubset(price_outcomes.columns)
    assert {
        "Condition_ID",
        "Sample_Size",
        "Average_Forward_Close_Return_Pips",
        "Direction_Alignment_Rate",
    }.issubset(summaries.columns)
    assert {"Return_Bucket", "Frequency", "Low_Sample_Size"}.issubset(distributions.columns)
    assert report_path.exists()

    report_text = report_path.read_text(encoding="utf-8")
    for term in FORBIDDEN_REPORT_TERMS:
        assert term not in report_text
