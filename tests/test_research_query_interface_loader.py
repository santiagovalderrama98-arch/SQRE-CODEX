from pathlib import Path

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.loader import ResearchQueryInterfaceDesignLoader


def test_loader_reads_required_reference_store(tmp_path: Path):
    reference_dir = tmp_path / "reference"
    usage_dir = tmp_path / "usage"
    reference_dir.mkdir()
    usage_dir.mkdir()
    (reference_dir / "research_reference_store.csv").write_text("Research_Reference_ID\nRRS_1\n", encoding="utf-8")
    config = ResearchQueryInterfaceDesignConfig(reference_store_dir=reference_dir, usage_review_dir=usage_dir)

    frames = ResearchQueryInterfaceDesignLoader(config).load_inputs()

    assert len(frames["reference_store"]) == 1
    assert frames["usage_scenarios"].empty

