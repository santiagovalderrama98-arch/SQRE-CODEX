from pathlib import Path

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.source_inventory import build_source_inventory


def test_source_inventory_marks_required_missing(tmp_path: Path):
    config = ResearchQueryInterfaceDesignConfig(reference_store_dir=tmp_path / "missing_reference", usage_review_dir=tmp_path / "usage")

    inventory = build_source_inventory(config)

    reference_store = next(row for row in inventory if row.source_name == "reference_store")
    assert reference_store.exists is False
    assert reference_store.load_status == "MISSING_REQUIRED"

