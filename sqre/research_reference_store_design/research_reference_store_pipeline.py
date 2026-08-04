"""Pipeline for Research Reference Store Design."""

from __future__ import annotations

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig
from sqre.research_reference_store_design.findings import build_summary
from sqre.research_reference_store_design.granularity_reference_review import build_granularity_reference_review
from sqre.research_reference_store_design.horizon_reference_review import build_horizon_reference_review
from sqre.research_reference_store_design.loader import ResearchReferenceStoreDesignLoader
from sqre.research_reference_store_design.models import ResearchReferenceStoreDesignResult
from sqre.research_reference_store_design.reference_candidate_builder import build_reference_candidates
from sqre.research_reference_store_design.reference_exclusion_review import build_reference_exclusion_review
from sqre.research_reference_store_design.reference_store_builder import build_reference_store
from sqre.research_reference_store_design.reports import write_outputs
from sqre.research_reference_store_design.source_inventory import build_source_inventory


class ResearchReferenceStoreDesignPipeline:
    """Run the research-only reference store design workflow."""

    def __init__(self, config: ResearchReferenceStoreDesignConfig) -> None:
        self.config = config
        self.loader = ResearchReferenceStoreDesignLoader(config)

    def run(self) -> ResearchReferenceStoreDesignResult:
        source_inventory = build_source_inventory(self.config)
        interpretability = self.loader.load_interpretability_review()
        directional = self.loader.load_directional_behavior_review()
        excursion = self.loader.load_excursion_behavior_review()
        horizon_stability = self.loader.load_horizon_stability_review()
        granularity_input = self.loader.load_context_granularity_review()
        interpretation_summary = self.loader.load_interpretation_summary()
        forward_profiles = self.loader.load_forward_outcome_profiles()
        sample_adequacy = self.loader.load_sample_adequacy_review()
        dispersion = self.loader.load_dispersion_review()
        aligned_summary = self.loader.load_aligned_summary()
        candidates = build_reference_candidates(interpretability, directional, excursion, horizon_stability, self.config)
        reference_store = build_reference_store(candidates)
        exclusion_review = build_reference_exclusion_review(candidates)
        granularity_review = build_granularity_reference_review(candidates)
        horizon_review = build_horizon_reference_review(candidates)
        summary = build_summary(candidates, reference_store, exclusion_review, granularity_review, horizon_review, self.config)
        result = ResearchReferenceStoreDesignResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=source_inventory,
            interpretability_review=interpretability,
            directional_behavior_review=directional,
            excursion_behavior_review=excursion,
            horizon_stability_review=horizon_stability,
            context_granularity_review=granularity_input,
            interpretation_summary=interpretation_summary,
            forward_outcome_profiles=forward_profiles,
            sample_adequacy_review=sample_adequacy,
            dispersion_review=dispersion,
            aligned_summary=aligned_summary,
            candidates=candidates,
            reference_store=reference_store,
            exclusion_review=exclusion_review,
            granularity_review=granularity_review,
            horizon_review=horizon_review,
            summary=summary,
        )
        return write_outputs(result)
