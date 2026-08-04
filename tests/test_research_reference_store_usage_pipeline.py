import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.research_reference_store_usage_pipeline import (
    ResearchReferenceStoreUsageReviewPipeline,
)


def test_pipeline_writes_expected_outputs(tmp_path):
    reference_dir = tmp_path / "reference"
    alignment_dir = tmp_path / "alignment"
    output_dir = tmp_path / "output"
    reference_dir.mkdir()
    alignment_dir.mkdir()
    _write_reference_store(reference_dir)
    _write_alignment(alignment_dir)
    config = ResearchReferenceStoreUsageReviewConfig(
        reference_store_dir=reference_dir,
        interpretation_dir=tmp_path / "missing_interpretation",
        same_time_alignment_dir=alignment_dir,
        output_dir=output_dir,
        report_path=output_dir / "research_reference_store_usage_review_report.txt",
        preferred_horizons=[1],
    )

    result = ResearchReferenceStoreUsageReviewPipeline(config).run()

    assert result.summary is not None
    assert result.summary.matched_scenario_count == 1
    assert (output_dir / "research_reference_lookup_results.csv").exists()
    assert (output_dir / "research_reference_store_usage_review_summary.csv").exists()
    assert result.report_path.exists()


def test_pipeline_handles_missing_inputs(tmp_path):
    output_dir = tmp_path / "output"
    config = ResearchReferenceStoreUsageReviewConfig(
        reference_store_dir=tmp_path / "missing_reference",
        interpretation_dir=tmp_path / "missing_interpretation",
        same_time_alignment_dir=tmp_path / "missing_alignment",
        output_dir=output_dir,
        report_path=output_dir / "report.txt",
    )

    result = ResearchReferenceStoreUsageReviewPipeline(config).run()

    assert result.summary is not None
    assert result.summary.research_reference_store_usage_readiness_flag == "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    assert (output_dir / "research_reference_usage_scenarios.csv").exists()


def _write_reference_store(path):
    pd.DataFrame(
        [
            {
                "Research_Reference_ID": "REF_1",
                "Symbol": "EURUSD",
                "H4_Timeframe": "H4",
                "D1_Timeframe": "D1",
                "Outcome_Profile_ID": "OUT_1",
                "Context_Granularity": "D1_STATE_REGIME",
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
                "Forward_Horizon_H4_Candles": 1,
                "Outcome_Sample_Size": 25,
                "Outcome_Dispersion_Pips": 30.0,
                "Directional_Behavior_Class": "MIXED",
                "Dominant_Observed_Direction": "UP",
                "Excursion_Behavior_Class": "BALANCED",
                "Horizon_Stability_Class": "STABLE",
                "Reference_Tier": "CORE_REFERENCE",
            }
        ]
    ).to_csv(path / "research_reference_store.csv", index=False)


def _write_alignment(path):
    pd.DataFrame(
        [
            {
                "H4_Transition_Label": "A_TO_B",
                "D1_Market_State": "D1_STATE",
                "D1_Regime_Label": "REGIME",
                "D1_Structure_Direction": "UP",
            }
        ]
    ).to_csv(path / "h4_transition_d1_same_time_alignment.csv", index=False)
