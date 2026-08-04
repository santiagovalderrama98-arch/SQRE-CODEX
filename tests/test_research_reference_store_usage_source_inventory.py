import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.source_inventory import build_source_inventory


def test_source_inventory_marks_loaded_and_missing_files(tmp_path):
    reference_dir = tmp_path / "reference"
    reference_dir.mkdir()
    pd.DataFrame([{"Research_Reference_ID": "REF_1"}]).to_csv(reference_dir / "research_reference_store.csv", index=False)
    config = ResearchReferenceStoreUsageReviewConfig(
        reference_store_dir=reference_dir,
        interpretation_dir=tmp_path / "missing_interpretation",
        same_time_alignment_dir=tmp_path / "missing_alignment",
    )

    rows = build_source_inventory(config)

    reference = next(row for row in rows if row.source_name == "reference_store")
    optional = next(row for row in rows if row.source_name == "transition_alignment")
    assert reference.load_status == "LOADED"
    assert reference.rows_loaded == 1
    assert optional.load_status == "MISSING"
