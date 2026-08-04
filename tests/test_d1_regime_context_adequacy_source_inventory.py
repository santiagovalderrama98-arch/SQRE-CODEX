from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.source_inventory import build_source_inventory
from tests.d1_regime_context_adequacy_test_utils import (
    write_contextual_transition_inputs,
    write_optional_supporting_inputs,
)


def test_source_inventory_marks_required_and_optional_sources(tmp_path):
    contextual_dir = tmp_path / "contextual"
    alignment_dir = tmp_path / "alignment"
    timestamped_dir = tmp_path / "timestamped"
    write_contextual_transition_inputs(contextual_dir)
    write_optional_supporting_inputs(alignment_dir, timestamped_dir)

    rows = build_source_inventory(contextual_dir, alignment_dir, timestamped_dir)

    required = [row for row in rows if row.source_type == "CONTEXTUAL_TRANSITION_INPUT"]
    optional = [row for row in rows if row.source_type == "OPTIONAL_SUPPORTING_DIAGNOSTIC"]
    assert len(required) == 6
    assert len(optional) == 5
    assert all(row.load_status == "LOADED" for row in required)
