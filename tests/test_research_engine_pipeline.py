from __future__ import annotations

import pandas as pd

from sqre.research_engine.config import ResearchEngineConfig
from sqre.research_engine.research_engine_pipeline import run_research_engine
from tests.research_test_utils import write_sample_inputs


def test_research_engine_pipeline_writes_all_outputs(tmp_path) -> None:
    states_path, transitions_path = write_sample_inputs(tmp_path)
    output_dir = tmp_path / "research"
    report_path = tmp_path / "reports" / "research_engine_report.txt"

    summary = run_research_engine(
        states_path=states_path,
        transitions_path=transitions_path,
        output_dir=output_dir,
        report_path=report_path,
        config=ResearchEngineConfig(forward_windows=[1, 2], minimum_sample_size=2),
    )

    assert summary.states_processed == 6
    assert summary.transitions_processed == 5
    assert summary.conditions_evaluated > 0
    assert summary.forward_state_rows > 0
    assert summary.forward_transition_rows > 0
    assert summary.preceding_state_rows > 0
    assert summary.sequence_outcome_rows > 0
    assert summary.condition_summary_rows == summary.conditions_evaluated

    expected_files = [
        "forward_state_distributions.csv",
        "forward_transition_distributions.csv",
        "preceding_state_distributions.csv",
        "sequence_outcomes.csv",
        "condition_summaries.csv",
    ]
    for filename in expected_files:
        assert (output_dir / filename).exists()
        assert not pd.read_csv(output_dir / filename).empty

    assert report_path.exists()
    assert "No trading signals" in report_path.read_text(encoding="utf-8")
