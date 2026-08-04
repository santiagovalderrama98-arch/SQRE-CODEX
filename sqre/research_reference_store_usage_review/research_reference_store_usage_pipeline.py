"""Pipeline for Research Reference Store Usage Review."""

from __future__ import annotations

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.evidence_quality_review import build_evidence_quality_review
from sqre.research_reference_store_usage_review.findings import build_summary
from sqre.research_reference_store_usage_review.granularity_usage_review import build_granularity_usage_review
from sqre.research_reference_store_usage_review.horizon_usage_review import build_horizon_usage_review
from sqre.research_reference_store_usage_review.loader import ResearchReferenceStoreUsageReviewLoader
from sqre.research_reference_store_usage_review.models import ResearchReferenceStoreUsageReviewResult
from sqre.research_reference_store_usage_review.reference_availability_review import build_reference_availability_review
from sqre.research_reference_store_usage_review.reference_lookup_engine import build_reference_lookup_results
from sqre.research_reference_store_usage_review.reports import write_outputs
from sqre.research_reference_store_usage_review.source_inventory import build_source_inventory
from sqre.research_reference_store_usage_review.usage_scenario_builder import build_usage_scenarios


class ResearchReferenceStoreUsageReviewPipeline:
    """Run the research-only reference-store usage review."""

    def __init__(self, config: ResearchReferenceStoreUsageReviewConfig) -> None:
        self.config = config
        self.loader = ResearchReferenceStoreUsageReviewLoader(config)

    def run(self) -> ResearchReferenceStoreUsageReviewResult:
        source_inventory = build_source_inventory(self.config)
        reference_store = self.loader.load_reference_store()
        reference_candidates = self.loader.load_reference_candidates()
        exclusion_review = self.loader.load_exclusion_review()
        reference_granularity_review = self.loader.load_reference_granularity_review()
        reference_horizon_review = self.loader.load_reference_horizon_review()
        reference_store_summary = self.loader.load_reference_store_summary()
        interpretability = self.loader.load_interpretability_review()
        directional = self.loader.load_directional_behavior_review()
        excursion = self.loader.load_excursion_behavior_review()
        horizon_stability = self.loader.load_horizon_stability_review()
        context_granularity = self.loader.load_context_granularity_review()
        interpretation_summary = self.loader.load_interpretation_summary()
        transition_alignment = self.loader.load_transition_alignment()
        state_alignment = self.loader.load_state_alignment()
        alignment_summary = self.loader.load_alignment_summary()
        scenarios = build_usage_scenarios(transition_alignment, reference_store, self.config)
        lookup_results = build_reference_lookup_results(scenarios, reference_store, self.config)
        availability = build_reference_availability_review(lookup_results, self.config)
        granularity_usage = build_granularity_usage_review(lookup_results, self.config)
        horizon_usage = build_horizon_usage_review(lookup_results, self.config)
        evidence_quality = build_evidence_quality_review(lookup_results)
        summary = build_summary(
            reference_store,
            scenarios,
            lookup_results,
            availability,
            granularity_usage,
            horizon_usage,
            self.config,
        )
        result = ResearchReferenceStoreUsageReviewResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=source_inventory,
            reference_store=reference_store,
            reference_candidates=reference_candidates,
            exclusion_review=exclusion_review,
            reference_granularity_review=reference_granularity_review,
            reference_horizon_review=reference_horizon_review,
            reference_store_summary=reference_store_summary,
            interpretability_review=interpretability,
            directional_behavior_review=directional,
            excursion_behavior_review=excursion,
            horizon_stability_review=horizon_stability,
            context_granularity_review=context_granularity,
            interpretation_summary=interpretation_summary,
            transition_alignment=transition_alignment,
            state_alignment=state_alignment,
            alignment_summary=alignment_summary,
            usage_scenarios=scenarios,
            lookup_results=lookup_results,
            availability_review=availability,
            granularity_usage_review=granularity_usage,
            horizon_usage_review=horizon_usage,
            evidence_quality_review=evidence_quality,
            summary=summary,
        )
        return write_outputs(result)
