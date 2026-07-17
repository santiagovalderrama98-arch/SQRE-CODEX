from pathlib import Path

from test_h4_transition_scenario_dispersion_profile_diagnostics import build_profile_dispersion_diagnostics
from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig
from sqre.h4_transition_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)
from sqre.h4_transition_scenario_dispersion_review.transition_state_dispersion import (
    build_source_state_dispersion_summary,
    build_target_state_dispersion_summary,
)


def test_source_and_target_state_summaries_aggregate_transition_profiles(tmp_path: Path):
    write_review_inputs(tmp_path)
    diagnostics = build_profile_dispersion_diagnostics(
        load_profile_inventory(tmp_path),
        load_outcome_statistics(tmp_path),
        load_scenario_comparisons(tmp_path),
        H4TransitionScenarioDispersionReviewConfig(),
    )

    source_rows = build_source_state_dispersion_summary(diagnostics)
    target_rows = build_target_state_dispersion_summary(diagnostics)

    source_displacement = next(row for row in source_rows if row.group_value == "DIRECTIONAL_DISPLACEMENT")
    target_displacement = next(row for row in target_rows if row.group_value == "DIRECTIONAL_DISPLACEMENT")
    assert source_displacement.profile_count == 2
    assert source_displacement.high_dispersion_profile_count == 1
    assert target_displacement.profile_count == 3
    assert target_displacement.sample_constrained_profile_count == 1
