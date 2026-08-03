from pathlib import Path

import pandas as pd

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.h4_timestamped_context_table_pipeline import (
    run_h4_timestamped_context_table_generation,
)


def test_pipeline_writes_all_expected_outputs(tmp_path: Path):
    combined = tmp_path / "combined"
    validation = tmp_path / "validation"
    scenario_dir = validation / "scn"
    research = tmp_path / "research"
    combined.mkdir()
    scenario_dir.mkdir(parents=True)
    research.mkdir()
    (combined / "h4_transition_state_context_inventory.csv").write_text(
        "Context_ID,Transition_Label,Forward_Window,Source_State,Target_State\nCTX_1,A -> B,12,A,B\n",
        encoding="utf-8",
    )
    (validation / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,Symbol,Timeframe,Period_Start,Period_End,Transitions_Generated\n"
        "SCN_1,EURUSD,H4,2026-01-01,2026-01-31,1\n",
        encoding="utf-8",
    )
    (scenario_dir / "state_transitions.csv").write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State,Transition_Label,Forward_Window\n"
        "SCN_1,2026-01-01 04:00:00,A,B,A -> B,12\n",
        encoding="utf-8",
    )
    config = H4TimestampedContextTableGenerationConfig(
        h4_combined_context_dir=combined,
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=research,
        output_dir=tmp_path / "out",
        report_path=tmp_path / "out/report.txt",
    )

    result = run_h4_timestamped_context_table_generation(config)

    expected = [
        "h4_timestamped_source_inventory.csv",
        "h4_timestamped_scenario_inventory.csv",
        "h4_timestamped_context_rows.csv",
        "h4_timestamped_context_coverage_review.csv",
        "h4_timestamped_missing_context_review.csv",
        "h4_timestamped_context_generation_summary.csv",
    ]
    assert all((result.output_dir / name).exists() for name in expected)
    summary = pd.read_csv(result.output_dir / "h4_timestamped_context_generation_summary.csv").iloc[0]
    assert summary["Timestamped_Context_Row_Count"] == 1
    assert summary["H4_Timestamped_Context_Readiness_Flag"] == "READY_FOR_H4_D1_TEMPORAL_ALIGNMENT"
