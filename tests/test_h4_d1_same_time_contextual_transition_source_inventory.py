from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.source_inventory import build_source_inventory
from tests.h4_d1_same_time_contextual_transition_test_utils import write_transition_alignment


def test_source_inventory_reports_loaded_and_missing_sources(tmp_path):
    same_time_dir = tmp_path / "same_time"
    optional_dir = tmp_path / "optional"
    write_transition_alignment(same_time_dir)

    rows = build_source_inventory(same_time_dir, optional_dir)
    statuses = {row.source_name: row.load_status for row in rows}

    assert statuses["h4_transition_d1_same_time_alignment"] == "LOADED"
    assert statuses["timestamped_h4_market_states"] == "MISSING"
