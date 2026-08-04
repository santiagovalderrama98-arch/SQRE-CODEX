from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.source_inventory import build_source_inventory
from tests.h4_d1_forward_outcome_interpretation_test_utils import write_phase_7515_inputs


def test_source_inventory_reports_loaded_and_missing_files(tmp_path):
    forward_dir = tmp_path / "forward"
    write_phase_7515_inputs(forward_dir)
    config = H4D1ForwardOutcomeInterpretationReviewConfig(
        forward_outcome_dir=forward_dir,
        contextual_transition_dir=tmp_path / "missing_context",
    )

    inventory = build_source_inventory(config)
    statuses = {row.source_name: row.load_status for row in inventory}

    assert statuses["h4_d1_forward_outcome_profiles"] == "LOADED"
    assert statuses["h4_d1_same_time_contextual_transition_profiles"] == "MISSING"
