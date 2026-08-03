from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.h4_timestamped_state_transition_pipeline import (
    run_h4_timestamped_state_transition_outputs,
)


def test_pipeline_writes_all_expected_outputs_and_report(tmp_path: Path):
    validation = tmp_path / "validation"
    scenario_dir = validation / "scenario"
    research = tmp_path / "research"
    scenario_dir.mkdir(parents=True)
    research.mkdir()
    (validation / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,Symbol,Timeframe,Period_Start,Period_End,States_Generated,Transitions_Generated\n"
        "SCN_1,EURUSD,H4,2026-01-01,2026-01-31,2,1\n",
        encoding="utf-8",
    )
    (scenario_dir / "market_states.csv").write_text(
        "Scenario_ID,State_Time,Market_State,Timeframe\n"
        "SCN_1,2026-01-01 00:00:00,A,H4\n"
        "SCN_1,2026-01-01 04:00:00,B,H4\n",
        encoding="utf-8",
    )
    config = H4TimestampedStateTransitionConfig(
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=research,
        validation_config=tmp_path / "missing.yaml",
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out/report.txt",
    )

    result = run_h4_timestamped_state_transition_outputs(config)

    expected = [
        "h4_timestamped_state_transition_source_inventory.csv",
        "h4_timestamped_state_transition_scenario_inventory.csv",
        "h4_timestamped_market_states.csv",
        "h4_timestamped_state_transitions.csv",
        "h4_timestamped_state_transition_coverage_review.csv",
        "h4_timestamped_state_transition_missing_output_review.csv",
        "h4_timestamped_state_transition_generation_summary.csv",
    ]
    assert all((result.output_dir / name).exists() for name in expected)
    summary = pd.read_csv(result.output_dir / "h4_timestamped_state_transition_generation_summary.csv").iloc[0]
    assert summary["Timestamped_State_Row_Count"] == 2
    assert summary["Timestamped_Transition_Row_Count"] == 1
    assert result.report_path.exists()
