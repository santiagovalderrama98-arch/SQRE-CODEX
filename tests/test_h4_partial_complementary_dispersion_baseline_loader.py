from pathlib import Path

import pandas as pd

from sqre.h4_partial_complementary_dispersion_review.baseline_dispersion_loader import (
    build_source_inventory,
    load_baseline_dispersion_snapshot,
)
from sqre.h4_partial_complementary_dispersion_review.config import (
    H4PartialComplementaryDispersionReviewConfig,
)


def test_baseline_loader_handles_missing_optional_directories_safely(tmp_path: Path):
    config = H4PartialComplementaryDispersionReviewConfig(
        partial_validation_dir=tmp_path / "partial",
        h4_state_dispersion_dir=tmp_path / "missing_state",
        h4_transition_dispersion_dir=tmp_path / "missing_transition",
    )

    inventory = build_source_inventory(config)
    snapshot = load_baseline_dispersion_snapshot(config)

    assert inventory
    assert snapshot.state_dispersion_profile == "BASELINE_UNAVAILABLE"
    assert snapshot.transition_dispersion_profile == "BASELINE_UNAVAILABLE"


def test_baseline_loader_reads_synthetic_transition_sensitivity_summary(tmp_path: Path):
    transition_dir = tmp_path / "transition_sensitive"
    transition_dir.mkdir()
    pd.DataFrame(
        [
            {
                "H4_Transition_Scenario_Sensitive_Profile": "HIGH_TRANSITION_SCENARIO_SENSITIVITY",
                "High_Sensitivity_Profile_Count": 12,
                "Near_Aggregation_Candidate_Count": 0,
            }
        ]
    ).to_csv(transition_dir / "h4_transition_scenario_sensitive_review_summary.csv", index=False)

    snapshot = load_baseline_dispersion_snapshot(
        H4PartialComplementaryDispersionReviewConfig(h4_transition_sensitive_dir=transition_dir)
    )

    assert snapshot.scenario_sensitive_profile == "HIGH_TRANSITION_SCENARIO_SENSITIVITY"
    assert snapshot.high_sensitivity_profile_count == 12
    assert snapshot.near_aggregation_candidate_count == 0
