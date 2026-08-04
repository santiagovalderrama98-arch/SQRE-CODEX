import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.loader import ResearchReferenceStoreUsageReviewLoader


def test_loader_returns_empty_frame_for_missing_reference_store(tmp_path):
    config = ResearchReferenceStoreUsageReviewConfig(reference_store_dir=tmp_path / "missing")
    loader = ResearchReferenceStoreUsageReviewLoader(config)

    assert loader.load_reference_store().empty


def test_loader_reads_reference_store(tmp_path):
    reference_dir = tmp_path / "reference"
    reference_dir.mkdir()
    pd.DataFrame([{"Research_Reference_ID": "REF_1"}]).to_csv(reference_dir / "research_reference_store.csv", index=False)
    config = ResearchReferenceStoreUsageReviewConfig(reference_store_dir=reference_dir)

    frame = ResearchReferenceStoreUsageReviewLoader(config).load_reference_store()

    assert len(frame) == 1
    assert frame.iloc[0]["Research_Reference_ID"] == "REF_1"
