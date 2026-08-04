"""Load inputs for Research Reference Store Design."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_reference_store_design.config import ResearchReferenceStoreDesignConfig


REQUIRED_FILES = {
    "interpretability_review": "h4_d1_outcome_profile_interpretability_review.csv",
    "directional_behavior_review": "h4_d1_directional_behavior_review.csv",
    "excursion_behavior_review": "h4_d1_excursion_behavior_review.csv",
    "horizon_stability_review": "h4_d1_horizon_stability_review.csv",
    "context_granularity_review": "h4_d1_context_granularity_utility_review.csv",
    "interpretation_summary": "h4_d1_forward_outcome_interpretation_review_summary.csv",
}

OPTIONAL_FILES = {
    "forward_outcome_profiles": "h4_d1_forward_outcome_profiles.csv",
    "sample_adequacy_review": "h4_d1_forward_outcome_sample_adequacy_review.csv",
    "dispersion_review": "h4_d1_forward_outcome_dispersion_review.csv",
    "aligned_summary": "h4_d1_aligned_forward_outcome_research_summary.csv",
}


class ResearchReferenceStoreDesignLoader:
    """Read required and optional CSV files without failing on missing inputs."""

    def __init__(self, config: ResearchReferenceStoreDesignConfig) -> None:
        self.config = config

    def load_required(self, name: str) -> pd.DataFrame:
        return self._load_frame(self.config.interpretation_dir / REQUIRED_FILES[name])

    def load_optional(self, name: str) -> pd.DataFrame:
        return self._load_frame(self.config.forward_outcome_dir / OPTIONAL_FILES[name])

    def load_interpretability_review(self) -> pd.DataFrame:
        return self.load_required("interpretability_review")

    def load_directional_behavior_review(self) -> pd.DataFrame:
        return self.load_required("directional_behavior_review")

    def load_excursion_behavior_review(self) -> pd.DataFrame:
        return self.load_required("excursion_behavior_review")

    def load_horizon_stability_review(self) -> pd.DataFrame:
        return self.load_required("horizon_stability_review")

    def load_context_granularity_review(self) -> pd.DataFrame:
        return self.load_required("context_granularity_review")

    def load_interpretation_summary(self) -> pd.DataFrame:
        return self.load_required("interpretation_summary")

    def load_forward_outcome_profiles(self) -> pd.DataFrame:
        return self.load_optional("forward_outcome_profiles")

    def load_sample_adequacy_review(self) -> pd.DataFrame:
        return self.load_optional("sample_adequacy_review")

    def load_dispersion_review(self) -> pd.DataFrame:
        return self.load_optional("dispersion_review")

    def load_aligned_summary(self) -> pd.DataFrame:
        return self.load_optional("aligned_summary")

    @staticmethod
    def _load_frame(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
