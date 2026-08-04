"""Pipeline for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.context_granularity_review import (
    build_context_granularity_utility_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.directional_behavior_review import (
    build_directional_behavior_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.excursion_behavior_review import (
    build_excursion_behavior_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.findings import build_summary
from sqre.h4_d1_forward_outcome_interpretation_review.horizon_stability_review import (
    build_horizon_stability_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.loader import H4D1ForwardOutcomeInterpretationLoader
from sqre.h4_d1_forward_outcome_interpretation_review.models import (
    H4D1ForwardOutcomeInterpretationReviewResult,
)
from sqre.h4_d1_forward_outcome_interpretation_review.profile_interpretability_review import (
    build_profile_interpretability_review,
)
from sqre.h4_d1_forward_outcome_interpretation_review.reports import write_outputs
from sqre.h4_d1_forward_outcome_interpretation_review.source_inventory import build_source_inventory


class H4D1ForwardOutcomeInterpretationReviewPipeline:
    """Run the descriptive H4/D1 forward outcome interpretation review."""

    def __init__(self, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> None:
        self.config = config
        self.loader = H4D1ForwardOutcomeInterpretationLoader(config)

    def run(self) -> H4D1ForwardOutcomeInterpretationReviewResult:
        source_inventory = build_source_inventory(self.config)
        forward_outcomes = self.loader.load_forward_outcomes()
        outcome_profiles = self.loader.load_outcome_profiles()
        dispersion_review = self.loader.load_dispersion_review()
        sample_adequacy_review = self.loader.load_sample_adequacy_review()
        aligned_summary = self.loader.load_aligned_summary()
        contextual_profiles = self.loader.load_contextual_profiles()
        contextual_sample_adequacy = self.loader.load_contextual_sample_adequacy()
        contextual_summary = self.loader.load_contextual_summary()
        interpretability_review = build_profile_interpretability_review(outcome_profiles, self.config)
        directional_behavior_review = build_directional_behavior_review(outcome_profiles, self.config)
        excursion_behavior_review = build_excursion_behavior_review(outcome_profiles, self.config)
        horizon_stability_review = build_horizon_stability_review(directional_behavior_review)
        context_granularity_review = build_context_granularity_utility_review(interpretability_review)
        summary = build_summary(
            interpretability_review,
            directional_behavior_review,
            horizon_stability_review,
            context_granularity_review,
            self.config,
        )
        result = H4D1ForwardOutcomeInterpretationReviewResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=source_inventory,
            forward_outcomes=forward_outcomes,
            outcome_profiles=outcome_profiles,
            dispersion_review=dispersion_review,
            sample_adequacy_review=sample_adequacy_review,
            aligned_summary=aligned_summary,
            contextual_profiles=contextual_profiles,
            contextual_sample_adequacy=contextual_sample_adequacy,
            contextual_summary=contextual_summary,
            interpretability_review=interpretability_review,
            directional_behavior_review=directional_behavior_review,
            excursion_behavior_review=excursion_behavior_review,
            horizon_stability_review=horizon_stability_review,
            context_granularity_review=context_granularity_review,
            summary=summary,
        )
        return write_outputs(result)
