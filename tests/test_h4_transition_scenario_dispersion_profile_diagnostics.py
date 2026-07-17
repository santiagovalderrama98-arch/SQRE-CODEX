from pathlib import Path

from test_h4_transition_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_transition_scenario_dispersion_review.config import H4TransitionScenarioDispersionReviewConfig
from sqre.h4_transition_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)
from sqre.h4_transition_scenario_dispersion_review.transition_profile_dispersion import (
    build_profile_dispersion_diagnostics,
)


def test_profile_diagnostics_compute_deviation_counts_and_classes(tmp_path: Path):
    write_review_inputs(tmp_path)

    rows = build_profile_dispersion_diagnostics(
        load_profile_inventory(tmp_path),
        load_outcome_statistics(tmp_path),
        load_scenario_comparisons(tmp_path),
        H4TransitionScenarioDispersionReviewConfig(),
    )

    expansion = next(
        row
        for row in rows
        if row.condition_label == "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_EXPANSION"
    )
    displacement = next(
        row
        for row in rows
        if row.condition_label == "DIRECTIONAL_DISPLACEMENT -> DIRECTIONAL_DISPLACEMENT"
    )
    assert expansion.high_deviation_scenario_count == 2
    assert expansion.dominant_deviation_class == "HIGH_DEVIATION"
    assert expansion.transition_profile_readiness_class == "SCENARIO_SENSITIVE_REVIEW"
    assert displacement.transition_profile_readiness_class == "AGGREGATION_CANDIDATE"
