from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.dashboard_reference_stability_review import build_dashboard_reference_stability_review
from sqre.reference_stability_validation.directional_consistency_review import build_directional_consistency_review
from sqre.reference_stability_validation.dispersion_stability_review import build_dispersion_stability_review
from sqre.reference_stability_validation.granularity_stability_review import build_granularity_stability_review
from sqre.reference_stability_validation.horizon_stability_review import build_horizon_stability_review
from sqre.reference_stability_validation.match_level_stability_review import build_match_level_stability_review
from sqre.reference_stability_validation.reference_population_review import build_reference_population_review
from sqre.reference_stability_validation.sample_adequacy_review import build_sample_adequacy_review
from sqre.reference_stability_validation.stability_scorecard_builder import build_stability_scorecard
from tests.test_reference_stability_validation_loader import dashboard_cards_frame, query_results_frame, reference_store_frame


def test_scorecard_summarizes_all_dimensions():
    config = ReferenceStabilityValidationConfig()
    store = reference_store_frame()
    scorecard = build_stability_scorecard(
        build_reference_population_review(config, store, False),
        build_horizon_stability_review(config, store),
        build_granularity_stability_review(config, store),
        build_sample_adequacy_review(config, store),
        build_dispersion_stability_review(config, store),
        build_directional_consistency_review(store),
        build_match_level_stability_review(config, query_results_frame()),
        build_dashboard_reference_stability_review(config, dashboard_cards_frame()),
    )

    assert len(scorecard) == 8
    assert "Reference Population" in set(scorecard["Stability_Dimension"])
