from pathlib import Path

from sqre.h4_d1_same_time_alignment_table.source_inventory import build_source_inventory
from tests.h4_d1_same_time_alignment_test_utils import write_same_time_alignment_fixture


def test_source_inventory_reports_loaded_sources(tmp_path: Path):
    timestamped_dir, synchronized_dir = write_same_time_alignment_fixture(tmp_path)

    rows = build_source_inventory(timestamped_dir, synchronized_dir)

    assert len(rows) == 5
    assert {row.load_status for row in rows} == {"LOADED"}


def test_source_inventory_reports_missing_sources(tmp_path: Path):
    rows = build_source_inventory(tmp_path / "timestamped", tmp_path / "sync")

    assert len(rows) == 5
    assert {row.load_status for row in rows} == {"MISSING"}
