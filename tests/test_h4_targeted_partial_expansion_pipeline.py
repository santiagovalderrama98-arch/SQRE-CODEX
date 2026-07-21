from pathlib import Path

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.h4_targeted_partial_expansion_validation_pipeline import (
    run_h4_targeted_partial_expansion_validation,
)
from sqre.h4_targeted_partial_expansion_validation.models import PartialValidationRunSummary

from test_h4_targeted_partial_expansion_helpers import write_baseline_inputs, write_feasibility_inputs, write_raw_ohlc


def test_pipeline_writes_all_expected_outputs(tmp_path: Path, monkeypatch):
    raw_file = write_raw_ohlc(tmp_path / "raw" / "EURUSD_H4_period_5_partial.csv")
    feasibility_dir = write_feasibility_inputs(tmp_path, raw_file=raw_file)
    baseline_validation_dir, baseline_research_dir = write_baseline_inputs(tmp_path)
    config = H4TargetedPartialExpansionValidationConfig(
        feasibility_dir=feasibility_dir,
        baseline_validation_dir=baseline_validation_dir,
        baseline_research_dir=baseline_research_dir,
        raw_data_dir=tmp_path / "raw",
        partial_data_dir=tmp_path / "raw",
        output_dir=tmp_path / "validation",
        research_output_dir=tmp_path / "research",
        report_path=tmp_path / "research" / "report.txt",
    )

    def fake_run(candidate, active_config):
        processed = active_config.output_dir / candidate.candidate_id / "processed"
        research = active_config.research_output_dir / candidate.candidate_id / "research"
        processed.mkdir(parents=True, exist_ok=True)
        research.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([{"Duration_Seconds": 100.0, "Price_Displacement": 0.0010}] * 20).to_csv(
            processed / "structures.csv",
            index=False,
        )
        pd.DataFrame([{"Market_State": "DIRECTIONAL_DISPLACEMENT"}] * 20).to_csv(
            processed / "market_states.csv",
            index=False,
        )
        pd.DataFrame([{"Transition_Label": "A -> B", "From_Market_State": "A", "To_Market_State": "B"}] * 10).to_csv(
            processed / "state_transitions.csv",
            index=False,
        )
        pd.DataFrame(
            [
                {
                    "Average_Forward_Range_Pips": 11,
                    "Average_Outcome_Magnitude_Pips": 7,
                    "Direction_Alignment_Rate": 0.5,
                    "Low_Sample_Size": False,
                }
            ]
        ).to_csv(research / "condition_price_outcome_summary.csv", index=False)
        return PartialValidationRunSummary(
            candidate.candidate_id,
            candidate.sample_label,
            "COMPLETED",
            "COMPLETED",
            "COMPLETED",
            "COMPLETED",
            "COMPLETED",
            "COMPLETED",
            "COMPLETED",
            100,
            50,
            20,
            20,
            10,
            1,
            "ok",
        )

    monkeypatch.setattr(
        "sqre.h4_targeted_partial_expansion_validation.h4_targeted_partial_expansion_validation_pipeline.run_partial_sample",
        fake_run,
    )

    result = run_h4_targeted_partial_expansion_validation(config)

    assert result.summary.validated_partial_candidate_count == 1
    expected = [
        "h4_partial_candidate_inventory.csv",
        "h4_partial_validation_run_summary.csv",
        "h4_partial_structure_state_summary.csv",
        "h4_partial_transition_summary.csv",
        "h4_partial_price_outcome_summary.csv",
        "h4_partial_vs_baseline_comparison.csv",
        "h4_partial_sample_adequacy_review.csv",
        "h4_targeted_partial_expansion_validation_summary.csv",
    ]
    for name in expected:
        assert (config.research_output_dir / name).exists()
    assert config.report_path.exists()


def test_pipeline_handles_missing_raw_without_generated_counts(tmp_path: Path):
    feasibility_dir = write_feasibility_inputs(tmp_path)
    baseline_validation_dir, baseline_research_dir = write_baseline_inputs(tmp_path)
    config = H4TargetedPartialExpansionValidationConfig(
        feasibility_dir=feasibility_dir,
        baseline_validation_dir=baseline_validation_dir,
        baseline_research_dir=baseline_research_dir,
        output_dir=tmp_path / "validation",
        research_output_dir=tmp_path / "research",
        report_path=tmp_path / "research" / "report.txt",
    )

    result = run_h4_targeted_partial_expansion_validation(config)

    assert result.run_summaries[0].run_status == "SKIPPED"
    assert result.sample_adequacy_rows[0].sample_adequacy_class == "PARTIAL_SAMPLE_UNAVAILABLE"
