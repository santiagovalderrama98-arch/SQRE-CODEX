from pathlib import Path

from test_h4_scenario_dispersion_review_loader import write_review_inputs
from sqre.h4_scenario_dispersion_review.config import H4ScenarioDispersionReviewConfig
from sqre.h4_scenario_dispersion_review.loader import (
    load_outcome_statistics,
    load_profile_inventory,
    load_scenario_comparisons,
)
from sqre.h4_scenario_dispersion_review.profile_dispersion import build_profile_dispersion_diagnostics


def test_profile_diagnostics_compute_deviation_counts_and_classes(tmp_path: Path):
    write_review_inputs(tmp_path)

    rows = build_profile_dispersion_diagnostics(
        load_profile_inventory(tmp_path),
        load_outcome_statistics(tmp_path),
        load_scenario_comparisons(tmp_path),
        H4ScenarioDispersionReviewConfig(),
    )

    displacement = next(row for row in rows if row.condition_label == "DIRECTIONAL_DISPLACEMENT")
    expansion = next(row for row in rows if row.condition_label == "DIRECTIONAL_EXPANSION")
    assert displacement.high_deviation_scenario_count == 2
    assert displacement.dominant_deviation_class == "HIGH_DEVIATION"
    assert displacement.profile_research_readiness_class == "SCENARIO_SENSITIVE_REVIEW"
    assert expansion.profile_research_readiness_class == "AGGREGATION_CANDIDATE"
