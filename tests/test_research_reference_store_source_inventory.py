from pathlib import Path

import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.source_inventory import build_source_inventory


def test_source_inventory_reports_loaded_and_missing_files(tmp_path: Path):
    interpretation_dir = tmp_path / "interpretation"
    forward_dir = tmp_path / "forward"
    interpretation_dir.mkdir()
    forward_dir.mkdir()
    pd.DataFrame([{"Outcome_Profile_ID": "OP_1"}]).to_csv(
        interpretation_dir / "h4_d1_outcome_profile_interpretability_review.csv", index=False
    )
    config = ResearchReferenceStoreDesignConfig(interpretation_dir=interpretation_dir, forward_outcome_dir=forward_dir)

    rows = build_source_inventory(config)
    loaded = [row for row in rows if row.source_name == "interpretability_review"][0]
    missing = [row for row in rows if row.source_name == "directional_behavior_review"][0]

    assert loaded.load_status == "LOADED"
    assert loaded.rows_loaded == 1
    assert missing.load_status == "MISSING"
