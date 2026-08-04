"""Load inputs for Research Query Interface Design."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig


REFERENCE_STORE_INPUTS = {
    "reference_store": "research_reference_store.csv",
    "reference_candidates": "research_reference_candidates.csv",
    "reference_granularity_review": "research_reference_granularity_review.csv",
    "reference_horizon_review": "research_reference_horizon_review.csv",
    "reference_store_summary": "research_reference_store_design_summary.csv",
}
USAGE_REVIEW_INPUTS = {
    "usage_lookup_results": "research_reference_lookup_results.csv",
    "usage_scenarios": "research_reference_usage_scenarios.csv",
    "usage_availability_review": "research_reference_availability_review.csv",
    "usage_granularity_review": "research_reference_granularity_usage_review.csv",
    "usage_horizon_review": "research_reference_horizon_usage_review.csv",
    "usage_evidence_quality_review": "research_reference_evidence_quality_review.csv",
    "usage_summary": "research_reference_store_usage_review_summary.csv",
}
INTERPRETATION_INPUTS = {
    "interpretability_review": "h4_d1_outcome_profile_interpretability_review.csv",
    "directional_behavior_review": "h4_d1_directional_behavior_review.csv",
    "excursion_behavior_review": "h4_d1_excursion_behavior_review.csv",
    "horizon_stability_review": "h4_d1_horizon_stability_review.csv",
    "context_granularity_review": "h4_d1_context_granularity_utility_review.csv",
    "interpretation_summary": "h4_d1_forward_outcome_interpretation_review_summary.csv",
}
ALIGNMENT_INPUTS = {
    "transition_alignment": "h4_transition_d1_same_time_alignment.csv",
    "state_alignment": "h4_state_d1_same_time_alignment.csv",
    "alignment_summary": "h4_d1_same_time_alignment_summary.csv",
}


class ResearchQueryInterfaceDesignLoader:
    """Read CSV inputs without failing on optional missing files."""

    def __init__(self, config: ResearchQueryInterfaceDesignConfig) -> None:
        self.config = config

    def load_inputs(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.reference_store_dir, REFERENCE_STORE_INPUTS))
        frames.update(self._load_group(self.config.usage_review_dir, USAGE_REVIEW_INPUTS))
        frames.update(self._load_group(self.config.interpretation_dir, INTERPRETATION_INPUTS))
        frames.update(self._load_group(self.config.same_time_alignment_dir, ALIGNMENT_INPUTS))
        return frames

    def _load_group(self, directory: Path, filenames: dict[str, str]) -> dict[str, pd.DataFrame]:
        return {name: self.load_frame(directory / filename) for name, filename in filenames.items()}

    @staticmethod
    def load_frame(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

