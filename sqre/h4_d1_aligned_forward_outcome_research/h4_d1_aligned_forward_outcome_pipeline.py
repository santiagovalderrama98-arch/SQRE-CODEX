"""Pipeline for H4/D1 aligned forward outcome research."""

from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.findings import build_summary
from sqre.h4_d1_aligned_forward_outcome_research.forward_outcome_calculator import calculate_forward_outcomes
from sqre.h4_d1_aligned_forward_outcome_research.h4_price_path_index import H4PricePathIndex
from sqre.h4_d1_aligned_forward_outcome_research.loader import (
    load_contextual_profiles,
    load_h4_ohlc,
    load_transition_alignment,
)
from sqre.h4_d1_aligned_forward_outcome_research.models import H4D1AlignedForwardOutcomeResearchResult
from sqre.h4_d1_aligned_forward_outcome_research.outcome_dispersion_review import build_dispersion_review
from sqre.h4_d1_aligned_forward_outcome_research.outcome_profile_builder import build_outcome_profiles
from sqre.h4_d1_aligned_forward_outcome_research.reports import write_outputs
from sqre.h4_d1_aligned_forward_outcome_research.sample_adequacy_review import build_sample_adequacy_review
from sqre.h4_d1_aligned_forward_outcome_research.source_inventory import build_source_inventory


class H4D1AlignedForwardOutcomeResearchPipeline:
    def __init__(self, config: H4D1AlignedForwardOutcomeResearchConfig) -> None:
        self.config = config

    def run(self) -> H4D1AlignedForwardOutcomeResearchResult:
        transition_alignment = load_transition_alignment(self.config.same_time_alignment_dir)
        h4_ohlc = load_h4_ohlc(self.config.synchronized_data_dir)
        price_index = H4PricePathIndex(h4_ohlc)
        forward_outcomes = calculate_forward_outcomes(transition_alignment, price_index, self.config)
        outcome_profiles = build_outcome_profiles(forward_outcomes, self.config)
        dispersion_review = build_dispersion_review(outcome_profiles)
        sample_adequacy_review = build_sample_adequacy_review(outcome_profiles, self.config)
        summary = build_summary(transition_alignment, forward_outcomes, outcome_profiles, self.config)
        result = H4D1AlignedForwardOutcomeResearchResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=build_source_inventory(
                self.config.same_time_alignment_dir,
                self.config.synchronized_data_dir,
                self.config.contextual_transition_dir,
            ),
            transition_alignment=transition_alignment,
            h4_ohlc=h4_ohlc,
            contextual_profiles=load_contextual_profiles(self.config.contextual_transition_dir),
            forward_outcomes=forward_outcomes,
            outcome_profiles=outcome_profiles,
            dispersion_review=dispersion_review,
            sample_adequacy_review=sample_adequacy_review,
            summary=summary,
        )
        return write_outputs(result)
