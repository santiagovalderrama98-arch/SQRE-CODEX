"""Pipeline for D1 regime context adequacy review."""

from __future__ import annotations

from sqre.d1_regime_context_adequacy_review.aggregation_candidate_review import (
    build_aggregation_candidate_review,
)
from sqre.d1_regime_context_adequacy_review.config import D1RegimeContextAdequacyReviewConfig
from sqre.d1_regime_context_adequacy_review.d1_context_inventory import build_d1_context_inventory
from sqre.d1_regime_context_adequacy_review.d1_context_sample_adequacy_review import (
    build_d1_context_sample_adequacy_review,
)
from sqre.d1_regime_context_adequacy_review.d1_fragmentation_review import build_fragmentation_review
from sqre.d1_regime_context_adequacy_review.h4_transition_sample_loss_review import build_sample_loss_review
from sqre.d1_regime_context_adequacy_review.loader import (
    load_concentration_review,
    load_contextual_sample_review,
    load_contextual_summary,
    load_market_state_distribution,
    load_profiles,
    load_regime_distribution,
)
from sqre.d1_regime_context_adequacy_review.models import D1RegimeContextAdequacyResult
from sqre.d1_regime_context_adequacy_review.readiness_classifier import build_summary
from sqre.d1_regime_context_adequacy_review.reports import write_outputs
from sqre.d1_regime_context_adequacy_review.source_inventory import build_source_inventory


class D1RegimeContextAdequacyPipeline:
    def __init__(self, config: D1RegimeContextAdequacyReviewConfig) -> None:
        self.config = config

    def run(self) -> D1RegimeContextAdequacyResult:
        profiles = load_profiles(self.config.contextual_transition_dir)
        concentration_review = load_concentration_review(self.config.contextual_transition_dir)
        d1_context_inventory = build_d1_context_inventory(profiles, self.config)
        fragmentation_review = build_fragmentation_review(profiles, concentration_review, self.config)
        sample_loss_review = build_sample_loss_review(profiles, self.config)
        d1_context_sample_adequacy_review = build_d1_context_sample_adequacy_review(d1_context_inventory)
        aggregation_candidate_review = build_aggregation_candidate_review(profiles, self.config)
        summary = build_summary(
            profiles,
            d1_context_inventory,
            fragmentation_review,
            sample_loss_review,
            aggregation_candidate_review,
            self.config,
        )
        result = D1RegimeContextAdequacyResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=build_source_inventory(
                self.config.contextual_transition_dir,
                self.config.same_time_alignment_dir,
                self.config.timestamped_state_regime_dir,
            ),
            profiles=profiles,
            market_state_distribution=load_market_state_distribution(self.config.contextual_transition_dir),
            regime_distribution=load_regime_distribution(self.config.contextual_transition_dir),
            concentration_review=concentration_review,
            contextual_sample_review=load_contextual_sample_review(self.config.contextual_transition_dir),
            contextual_summary=load_contextual_summary(self.config.contextual_transition_dir),
            d1_context_inventory=d1_context_inventory,
            fragmentation_review=fragmentation_review,
            sample_loss_review=sample_loss_review,
            d1_context_sample_adequacy_review=d1_context_sample_adequacy_review,
            aggregation_candidate_review=aggregation_candidate_review,
            summary=summary,
        )
        return write_outputs(result)
