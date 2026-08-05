import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.source_inventory import build_source_inventory


def test_source_inventory_marks_required_loaded_and_optional_missing(tmp_path):
    ref = tmp_path / "reference"
    query = tmp_path / "query"
    ref.mkdir()
    query.mkdir()
    pd.DataFrame([{"Research_Reference_ID": "RRS_1"}]).to_csv(ref / "research_reference_store.csv", index=False)
    pd.DataFrame([{"Research_Query_ID": "RQ_1"}]).to_csv(query / "research_query_requests.csv", index=False)
    config = CurrentMarketStateSnapshotResearchConfig(
        reference_store_dir=ref,
        query_interface_dir=query,
        usage_review_dir=tmp_path / "usage",
        same_time_alignment_dir=tmp_path / "alignment",
        timestamped_state_regime_dir=tmp_path / "timestamped",
    )

    rows = build_source_inventory(config)

    statuses = {row.source_name: row.load_status for row in rows}
    assert statuses["reference_store"] == "LOADED"
    assert statuses["query_requests_input"] == "LOADED"
    assert statuses["usage_scenarios"] == "INPUT_MISSING"
