from pathlib import Path

from test_h4_scenario_dispersion_profile_diagnostics import build_profile_dispersion_diagnostics
from test_h4_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_scenario_dispersion_review.config import H4ScenarioDispersionReviewConfig
from sqre.h4_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)
from sqre.h4_scenario_dispersion_review.state_dispersion import build_state_dispersion_summary


def test_state_summary_aggregates_state_profiles(tmp_path: Path):
    write_review_inputs(tmp_path)
    diagnostics = build_profile_dispersion_diagnostics(
        load_profile_inventory(tmp_path),
        load_outcome_statistics(tmp_path),
        load_scenario_comparisons(tmp_path),
        H4ScenarioDispersionReviewConfig(),
    )

    rows = build_state_dispersion_summary(diagnostics)

    displacement = next(row for row in rows if row.condition_label == "DIRECTIONAL_DISPLACEMENT")
    assert displacement.profile_count == 1
    assert displacement.high_dispersion_profile_count == 1
