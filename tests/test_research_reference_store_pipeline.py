from pathlib import Path

import pandas as pd

from sqre.research_reference_store_design import (
    ResearchReferenceStoreDesignConfig,
    ResearchReferenceStoreDesignPipeline,
)


def test_pipeline_writes_all_expected_outputs_and_report(tmp_path: Path):
    interpretation_dir = tmp_path / "interpretation"
    forward_dir = tmp_path / "forward"
    output_dir = tmp_path / "output"
    _write_synthetic_inputs(interpretation_dir, forward_dir)
    config = ResearchReferenceStoreDesignConfig(
        interpretation_dir=interpretation_dir,
        forward_outcome_dir=forward_dir,
        output_dir=output_dir,
        report_path=output_dir / "research_reference_store_design_report.txt",
    )

    result = ResearchReferenceStoreDesignPipeline(config).run()

    expected = [
        "research_reference_store_source_inventory.csv",
        "research_reference_candidates.csv",
        "research_reference_store.csv",
        "research_reference_exclusion_review.csv",
        "research_reference_granularity_review.csv",
        "research_reference_horizon_review.csv",
        "research_reference_store_design_summary.csv",
        "research_reference_store_design_report.txt",
    ]
    for filename in expected:
        assert (output_dir / filename).exists()
    assert result.summary is not None
    assert result.summary.reference_candidate_count == 4
    assert result.summary.included_reference_count == 2


def _write_synthetic_inputs(interpretation_dir: Path, forward_dir: Path) -> None:
    interpretation_dir.mkdir()
    forward_dir.mkdir()
    pd.DataFrame(
        [
            _profile("OP_1", "H4_TRANSITION_ONLY", "A", 3, 30, 20, "ADEQUATE_SAMPLE", "INTERPRETABLE_OUTCOME_PROFILE"),
            _profile("OP_2", "H4_TRANSITION_ONLY", "A", 6, 12, 50, "MODERATE_SAMPLE", "MODERATELY_INTERPRETABLE_OUTCOME_PROFILE"),
            _profile("OP_3", "D1_STATE", "B", 3, 5, 10, "LOW_SAMPLE", "NOT_INTERPRETABLE_SAMPLE_CONSTRAINED"),
            _profile("OP_4", "D1_STATE", "C", 6, 25, 100, "ADEQUATE_SAMPLE", "NOT_INTERPRETABLE_HIGH_DISPERSION"),
        ]
    ).to_csv(interpretation_dir / "h4_d1_outcome_profile_interpretability_review.csv", index=False)
    pd.DataFrame(
        [
            {"Outcome_Profile_ID": f"OP_{i}", "Directional_Behavior_Class": "OBSERVED_MIXED_DIRECTIONAL_BEHAVIOR", "Dominant_Observed_Direction": "OBSERVED_MIXED"}
            for i in range(1, 5)
        ]
    ).to_csv(interpretation_dir / "h4_d1_directional_behavior_review.csv", index=False)
    pd.DataFrame(
        [{"Outcome_Profile_ID": f"OP_{i}", "Excursion_Behavior_Class": "BALANCED_EXCURSION_BEHAVIOR"} for i in range(1, 5)]
    ).to_csv(interpretation_dir / "h4_d1_excursion_behavior_review.csv", index=False)
    pd.DataFrame(
        [
            {"Context_Granularity": "H4_TRANSITION_ONLY", "H4_Transition_Label": "A", "D1_Market_State": "", "D1_Regime_Label": "", "Horizon_Stability_Class": "STABLE_ACROSS_HORIZONS"},
            {"Context_Granularity": "D1_STATE", "H4_Transition_Label": "B", "D1_Market_State": "", "D1_Regime_Label": "", "Horizon_Stability_Class": "UNSTABLE_ACROSS_HORIZONS"},
        ]
    ).to_csv(interpretation_dir / "h4_d1_horizon_stability_review.csv", index=False)
    pd.DataFrame([{"Context_Granularity": "H4_TRANSITION_ONLY"}]).to_csv(
        interpretation_dir / "h4_d1_context_granularity_utility_review.csv", index=False
    )
    pd.DataFrame([{"Outcome_Profile_Count": 4}]).to_csv(
        interpretation_dir / "h4_d1_forward_outcome_interpretation_review_summary.csv", index=False
    )
    for filename in [
        "h4_d1_forward_outcome_profiles.csv",
        "h4_d1_forward_outcome_sample_adequacy_review.csv",
        "h4_d1_forward_outcome_dispersion_review.csv",
        "h4_d1_aligned_forward_outcome_research_summary.csv",
    ]:
        pd.DataFrame([{"Diagnostic": "synthetic"}]).to_csv(forward_dir / filename, index=False)


def _profile(
    profile_id: str,
    granularity: str,
    transition: str,
    horizon: int,
    sample_size: int,
    dispersion: float,
    sample_class: str,
    interpretability: str,
) -> dict[str, object]:
    return {
        "Outcome_Profile_ID": profile_id,
        "Symbol": "EURUSD",
        "H4_Timeframe": "H4",
        "D1_Timeframe": "D1",
        "Context_Granularity": granularity,
        "H4_Transition_Label": transition,
        "D1_Market_State": "",
        "D1_Regime_Label": "",
        "D1_Structure_Direction": "",
        "Forward_Horizon_H4_Candles": horizon,
        "Outcome_Sample_Size": sample_size,
        "Mean_Forward_Close_Change_Pips": 1.0,
        "Median_Forward_Close_Change_Pips": 0.5,
        "Outcome_Dispersion_Pips": dispersion,
        "Outcome_Sample_Adequacy_Class": sample_class,
        "Outcome_Interpretability_Class": interpretability,
    }
