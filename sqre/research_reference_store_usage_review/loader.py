"""Load inputs for Research Reference Store Usage Review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig


REFERENCE_STORE_FILES = {
    "reference_store": "research_reference_store.csv",
    "reference_candidates": "research_reference_candidates.csv",
    "exclusion_review": "research_reference_exclusion_review.csv",
    "reference_granularity_review": "research_reference_granularity_review.csv",
    "reference_horizon_review": "research_reference_horizon_review.csv",
    "reference_store_summary": "research_reference_store_design_summary.csv",
}
INTERPRETATION_FILES = {
    "interpretability_review": "h4_d1_outcome_profile_interpretability_review.csv",
    "directional_behavior_review": "h4_d1_directional_behavior_review.csv",
    "excursion_behavior_review": "h4_d1_excursion_behavior_review.csv",
    "horizon_stability_review": "h4_d1_horizon_stability_review.csv",
    "context_granularity_review": "h4_d1_context_granularity_utility_review.csv",
    "interpretation_summary": "h4_d1_forward_outcome_interpretation_review_summary.csv",
}
ALIGNMENT_FILES = {
    "transition_alignment": "h4_transition_d1_same_time_alignment.csv",
    "state_alignment": "h4_state_d1_same_time_alignment.csv",
    "alignment_summary": "h4_d1_same_time_alignment_summary.csv",
}


class ResearchReferenceStoreUsageReviewLoader:
    """Read required and optional CSV inputs without raising on missing files."""

    def __init__(self, config: ResearchReferenceStoreUsageReviewConfig) -> None:
        self.config = config

    def load_reference_store(self) -> pd.DataFrame:
        return self._load_frame(self.config.reference_store_dir / REFERENCE_STORE_FILES["reference_store"])

    def load_reference_candidates(self) -> pd.DataFrame:
        return self._load_frame(self.config.reference_store_dir / REFERENCE_STORE_FILES["reference_candidates"])

    def load_exclusion_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.reference_store_dir / REFERENCE_STORE_FILES["exclusion_review"])

    def load_reference_granularity_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.reference_store_dir / REFERENCE_STORE_FILES["reference_granularity_review"])

    def load_reference_horizon_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.reference_store_dir / REFERENCE_STORE_FILES["reference_horizon_review"])

    def load_reference_store_summary(self) -> pd.DataFrame:
        return self._load_frame(self.config.reference_store_dir / REFERENCE_STORE_FILES["reference_store_summary"])

    def load_interpretability_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / INTERPRETATION_FILES["interpretability_review"])

    def load_directional_behavior_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / INTERPRETATION_FILES["directional_behavior_review"])

    def load_excursion_behavior_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / INTERPRETATION_FILES["excursion_behavior_review"])

    def load_horizon_stability_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / INTERPRETATION_FILES["horizon_stability_review"])

    def load_context_granularity_review(self) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / INTERPRETATION_FILES["context_granularity_review"])

    def load_interpretation_summary(self) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / INTERPRETATION_FILES["interpretation_summary"])

    def load_transition_alignment(self) -> pd.DataFrame:
        return self._load_frame(self.config.same_time_alignment_dir / ALIGNMENT_FILES["transition_alignment"])

    def load_state_alignment(self) -> pd.DataFrame:
        return self._load_frame(self.config.same_time_alignment_dir / ALIGNMENT_FILES["state_alignment"])

    def load_alignment_summary(self) -> pd.DataFrame:
        return self._load_frame(self.config.same_time_alignment_dir / ALIGNMENT_FILES["alignment_summary"])

    @staticmethod
    def _load_frame(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
