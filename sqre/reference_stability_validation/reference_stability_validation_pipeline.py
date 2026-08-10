"""Pipeline for SQRE reference stability validation."""

from __future__ import annotations

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig
from sqre.reference_stability_validation.dashboard_reference_stability_review import (
    build_dashboard_reference_stability_review,
)
from sqre.reference_stability_validation.directional_consistency_review import build_directional_consistency_review
from sqre.reference_stability_validation.dispersion_stability_review import build_dispersion_stability_review
from sqre.reference_stability_validation.findings import build_summary
from sqre.reference_stability_validation.granularity_stability_review import build_granularity_stability_review
from sqre.reference_stability_validation.horizon_stability_review import build_horizon_stability_review
from sqre.reference_stability_validation.loader import ReferenceStabilityValidationLoader
from sqre.reference_stability_validation.match_level_stability_review import build_match_level_stability_review
from sqre.reference_stability_validation.models import ReferenceStabilityValidationResult
from sqre.reference_stability_validation.reference_population_review import build_reference_population_review
from sqre.reference_stability_validation.reports import write_outputs
from sqre.reference_stability_validation.sample_adequacy_review import build_sample_adequacy_review
from sqre.reference_stability_validation.source_inventory import build_source_inventory, has_missing_required_inputs
from sqre.reference_stability_validation.stability_scorecard_builder import build_stability_scorecard


class ReferenceStabilityValidationPipeline:
    """Run reference stability validation and write research diagnostics."""

    def __init__(self, config: ReferenceStabilityValidationConfig) -> None:
        self.config = config

    def run(self) -> ReferenceStabilityValidationResult:
        loader = ReferenceStabilityValidationLoader(self.config)
        frames = loader.load_frames()
        source_inventory = build_source_inventory(self.config)
        missing_required = has_missing_required_inputs(source_inventory)
        reference_store = frames.get("reference_store")
        query_results = frames.get("query_results")
        dashboard_cards = frames.get("dashboard_reference_cards")
        manual_summary = frames.get("manual_dashboard_review_summary")

        population = build_reference_population_review(self.config, reference_store, missing_required)
        horizon = build_horizon_stability_review(self.config, reference_store)
        granularity = build_granularity_stability_review(self.config, reference_store)
        sample = build_sample_adequacy_review(self.config, reference_store)
        dispersion = build_dispersion_stability_review(self.config, reference_store)
        directional = build_directional_consistency_review(reference_store)
        match_level = build_match_level_stability_review(self.config, query_results)
        dashboard = build_dashboard_reference_stability_review(self.config, dashboard_cards)
        scorecard = build_stability_scorecard(
            population,
            horizon,
            granularity,
            sample,
            dispersion,
            directional,
            match_level,
            dashboard,
        )
        summary = build_summary(
            self.config,
            source_inventory,
            population,
            horizon,
            granularity,
            sample,
            dispersion,
            match_level,
            dashboard,
            query_results,
            manual_summary,
        )
        result = ReferenceStabilityValidationResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            frames=frames,
            source_inventory=source_inventory,
            reference_population_review=population,
            horizon_stability_review=horizon,
            granularity_stability_review=granularity,
            sample_adequacy_review=sample,
            dispersion_stability_review=dispersion,
            directional_consistency_review=directional,
            match_level_stability_review=match_level,
            dashboard_reference_stability_review=dashboard,
            reference_stability_scorecard=scorecard,
            summary=summary,
        )
        return write_outputs(result)
