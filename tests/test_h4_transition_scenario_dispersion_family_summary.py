from pathlib import Path

from test_h4_transition_scenario_dispersion_profile_diagnostics import build_profile_dispersion_diagnostics
from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig
from sqre.h4_transition_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)
from sqre.h4_transition_scenario_dispersion_review.transition_family_dispersion import (
    build_transition_family_dispersion_summary,
)


def test_transition_family_summary_aggregates_transition_profiles(tmp_path: Path):
    write_review_inputs(tmp_path)
    diagnostics = build_profile_dispersion_diagnostics(
        load_profile_inventory(tmp_path),
        load_outcome_statistics(tmp_path),
        load_scenario_comparisons(tmp_path),
        H4TransitionScenarioDispersionReviewConfig(),
    )

    rows = build_transition_family_dispersion_summary(diagnostics)

    directional = next(row for row in rows if row.group_value == "DIRECTIONAL_TO_DIRECTIONAL")
    assert directional.profile_count == 3
    assert directional.high_dispersion_profile_count == 1
    assert directional.aggregation_candidate_profile_count == 2
