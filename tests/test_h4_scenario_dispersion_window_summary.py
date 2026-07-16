from pathlib import Path

from test_h4_scenario_dispersion_profile_diagnostics import build_profile_dispersion_diagnostics
from test_h4_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_scenario_dispersion_review.config import H4ScenarioDispersionReviewConfig
from sqre.h4_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)
from sqre.h4_scenario_dispersion_review.window_dispersion import build_window_dispersion_summary


def test_forward_window_summary_aggregates_window_profiles(tmp_path: Path):
    write_review_inputs(tmp_path)
    diagnostics = build_profile_dispersion_diagnostics(
        load_profile_inventory(tmp_path),
        load_outcome_statistics(tmp_path),
        load_scenario_comparisons(tmp_path),
        H4ScenarioDispersionReviewConfig(),
    )

    rows = build_window_dispersion_summary(diagnostics)

    fw3 = next(row for row in rows if row.forward_window == 3)
    assert fw3.profile_count == 2
    assert fw3.high_dispersion_profile_count == 1
