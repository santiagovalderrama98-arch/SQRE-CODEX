from pathlib import Path

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.research_query_interface_pipeline import ResearchQueryInterfaceDesignPipeline


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    reference_dir = tmp_path / "reference"
    usage_dir = tmp_path / "usage"
    output_dir = tmp_path / "output"
    reference_dir.mkdir()
    usage_dir.mkdir()
    (reference_dir / "research_reference_store.csv").write_text(
        "Research_Reference_ID,Outcome_Profile_ID,Context_Granularity,H4_Transition_Label,D1_Market_State,D1_Regime_Label,D1_Structure_Direction,Forward_Horizon_H4_Candles,Outcome_Sample_Size,Outcome_Dispersion_Pips,Reference_Tier\n"
        "RRS_1,OP_1,EXACT,A_TO_B,STATE,REGIME,UP,1,30,20,CORE_REFERENCE\n",
        encoding="utf-8",
    )
    (usage_dir / "research_reference_usage_scenarios.csv").write_text(
        "H4_Transition_Label,D1_Market_State,D1_Regime_Label,D1_Structure_Direction,Forward_Horizon_H4_Candles\n"
        "A_TO_B,STATE,REGIME,UP,1\n",
        encoding="utf-8",
    )
    config = ResearchQueryInterfaceDesignConfig(reference_store_dir=reference_dir, usage_review_dir=usage_dir, output_dir=output_dir, report_path=output_dir / "report.txt")

    result = ResearchQueryInterfaceDesignPipeline(config).run()

    assert result.summary is not None
    assert (output_dir / "research_query_results.csv").exists()
    assert (output_dir / "research_query_interface_design_summary.csv").exists()

