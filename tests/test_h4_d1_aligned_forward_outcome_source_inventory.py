from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.source_inventory import build_source_inventory
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_source_inventory_reports_loaded_and_missing_files(tmp_path):
    alignment_dir, synchronized_dir, contextual_dir = write_forward_outcome_inputs(tmp_path)

    rows = build_source_inventory(alignment_dir, synchronized_dir, contextual_dir)

    assert any(row.source_name == "h4_normalized_ohlc" and row.load_status == "LOADED" for row in rows)
    missing_rows = build_source_inventory(tmp_path / "empty_a", tmp_path / "empty_s", tmp_path / "empty_c")
    assert any(row.load_status == "MISSING" for row in missing_rows)
