from pathlib import Path

import pandas as pd

from sqre.research_reference_store_design import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.loader import ResearchReferenceStoreDesignLoader


def test_loader_handles_missing_inputs_safely(tmp_path: Path):
    config = ResearchReferenceStoreDesignConfig(
        interpretation_dir=tmp_path / "missing_interpretation",
        forward_outcome_dir=tmp_path / "missing_forward",
    )

    loader = ResearchReferenceStoreDesignLoader(config)

    assert loader.load_interpretability_review().empty
    assert loader.load_forward_outcome_profiles().empty


def test_loader_loads_interpretation_review_files(tmp_path: Path):
    interpretation_dir = tmp_path / "interpretation"
    interpretation_dir.mkdir()
    pd.DataFrame([{"Outcome_Profile_ID": "OP_1"}]).to_csv(
        interpretation_dir / "h4_d1_outcome_profile_interpretability_review.csv", index=False
    )
    config = ResearchReferenceStoreDesignConfig(interpretation_dir=interpretation_dir)

    frame = ResearchReferenceStoreDesignLoader(config).load_interpretability_review()

    assert frame["Outcome_Profile_ID"].tolist() == ["OP_1"]
