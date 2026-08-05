import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.current_market_state_snapshot_pipeline import (
    CurrentMarketStateSnapshotResearchPipeline,
)


def test_pipeline_runs_user_supplied_snapshot_with_synthetic_reference_store(tmp_path):
    ref = tmp_path / "reference"
    query = tmp_path / "query"
    out = tmp_path / "out"
    ref.mkdir()
    query.mkdir()
    pd.DataFrame([_reference()]).to_csv(ref / "research_reference_store.csv", index=False)
    pd.DataFrame([{"Research_Query_ID": "RQ_1"}]).to_csv(query / "research_query_requests.csv", index=False)
    config = CurrentMarketStateSnapshotResearchConfig(
        reference_store_dir=ref,
        query_interface_dir=query,
        usage_review_dir=tmp_path / "usage",
        same_time_alignment_dir=tmp_path / "alignment",
        timestamped_state_regime_dir=tmp_path / "timestamped",
        output_dir=out,
        report_path=out / "report.txt",
        snapshot_mode="USER_SUPPLIED_SNAPSHOT",
        snapshot_h4_transition_label="A_TO_B",
        snapshot_d1_market_state="STATE",
        snapshot_d1_regime_label="REGIME",
        snapshot_forward_horizon=1,
    )

    result = CurrentMarketStateSnapshotResearchPipeline(config).run()

    assert result.summary is not None
    assert result.summary.snapshot_query_with_result_count == 1
    assert (out / "current_market_state_snapshot_reference_results.csv").exists()


def _reference() -> dict[str, object]:
    return {
        "Research_Reference_ID": "RRS_1",
        "Outcome_Profile_ID": "OP_1",
        "Context_Granularity": "EXACT",
        "Reference_Tier": "CORE_REFERENCE",
        "H4_Transition_Label": "A_TO_B",
        "D1_Market_State": "STATE",
        "D1_Regime_Label": "REGIME",
        "D1_Structure_Direction": "UP",
        "Forward_Horizon_H4_Candles": 1,
        "Outcome_Sample_Size": 30,
        "Outcome_Dispersion_Pips": 20,
    }
