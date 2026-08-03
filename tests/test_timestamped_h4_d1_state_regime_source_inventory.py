from pathlib import Path

from sqre.timestamped_h4_d1_state_regime_generation.source_inventory import build_source_inventory
from tests.timestamped_h4_d1_state_regime_test_utils import write_synchronized_fixture


def test_source_inventory_reports_loaded_sources(tmp_path: Path):
    input_dir = write_synchronized_fixture(tmp_path / "sync")

    rows = build_source_inventory(input_dir)

    assert len(rows) == 4
    assert {row.load_status for row in rows} == {"LOADED"}


def test_source_inventory_reports_missing_sources(tmp_path: Path):
    rows = build_source_inventory(tmp_path / "missing")

    assert len(rows) == 4
    assert {row.load_status for row in rows} == {"MISSING"}
