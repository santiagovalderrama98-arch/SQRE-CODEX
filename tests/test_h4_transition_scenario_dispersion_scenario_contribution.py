from pathlib import Path

from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig
from sqre.h4_transition_scenario_dispersion_review.loader import load_scenario_comparisons
from sqre.h4_transition_scenario_dispersion_review.transition_scenario_contribution import build_scenario_contributions


def test_scenario_contribution_summary_computes_high_deviation_ratios(tmp_path: Path):
    write_review_inputs(tmp_path)

    rows = build_scenario_contributions(load_scenario_comparisons(tmp_path), H4TransitionScenarioDispersionReviewConfig())

    scenario_1 = next(row for row in rows if row.scenario_id == "S1")
    assert scenario_1.profile_count == 4
    assert scenario_1.high_deviation_profile_count == 1
    assert scenario_1.high_deviation_profile_ratio == 0.25
    assert scenario_1.scenario_contribution_class == "MODERATE_CONTRIBUTION"
