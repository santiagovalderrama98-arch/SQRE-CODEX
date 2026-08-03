"""Pipeline for H4/D1 same-time contextual transition review."""

from __future__ import annotations

from sqre.h4_d1_same_time_contextual_transition_review.config import (
    H4D1SameTimeContextualTransitionReviewConfig,
)
from sqre.h4_d1_same_time_contextual_transition_review.contextual_concentration_review import (
    build_context_concentration_review,
)
from sqre.h4_d1_same_time_contextual_transition_review.contextual_transition_profiler import (
    build_contextual_transition_profiles,
)
from sqre.h4_d1_same_time_contextual_transition_review.d1_context_distribution_review import (
    build_market_state_distribution_review,
)
from sqre.h4_d1_same_time_contextual_transition_review.loader import (
    load_alignment_summary,
    load_coverage_review,
    load_state_alignment,
    load_transition_alignment,
)
from sqre.h4_d1_same_time_contextual_transition_review.models import (
    H4D1SameTimeContextualTransitionReviewResult,
)
from sqre.h4_d1_same_time_contextual_transition_review.readiness_classifier import build_summary
from sqre.h4_d1_same_time_contextual_transition_review.regime_context_review import (
    build_regime_distribution_review,
)
from sqre.h4_d1_same_time_contextual_transition_review.reports import write_outputs
from sqre.h4_d1_same_time_contextual_transition_review.sample_adequacy_review import (
    build_sample_adequacy_review,
)
from sqre.h4_d1_same_time_contextual_transition_review.source_inventory import build_source_inventory


class H4D1SameTimeContextualTransitionReviewPipeline:
    def __init__(self, config: H4D1SameTimeContextualTransitionReviewConfig) -> None:
        self.config = config

    def run(self) -> H4D1SameTimeContextualTransitionReviewResult:
        transition_alignment = load_transition_alignment(self.config.same_time_alignment_dir)
        profiles = build_contextual_transition_profiles(transition_alignment, self.config)
        market_state_distribution = build_market_state_distribution_review(profiles, self.config)
        regime_distribution = build_regime_distribution_review(profiles, self.config)
        concentration_review = build_context_concentration_review(profiles, self.config)
        sample_adequacy_review = build_sample_adequacy_review(profiles, self.config)
        summary = build_summary(profiles, concentration_review, self.config)
        result = H4D1SameTimeContextualTransitionReviewResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=build_source_inventory(
                self.config.same_time_alignment_dir,
                self.config.timestamped_state_regime_dir,
            ),
            transition_alignment=transition_alignment,
            state_alignment=load_state_alignment(self.config.same_time_alignment_dir),
            coverage_review=load_coverage_review(self.config.same_time_alignment_dir),
            alignment_summary=load_alignment_summary(self.config.same_time_alignment_dir),
            contextual_profiles=profiles,
            market_state_distribution=market_state_distribution,
            regime_distribution=regime_distribution,
            concentration_review=concentration_review,
            sample_adequacy_review=sample_adequacy_review,
            summary=summary,
        )
        return write_outputs(result)
