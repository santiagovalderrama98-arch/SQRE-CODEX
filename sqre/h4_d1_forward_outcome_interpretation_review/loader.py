"""Input loading for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.source_inventory import expected_input_paths


class H4D1ForwardOutcomeInterpretationLoader:
    """Load required and optional Phase 7.5.15 outputs safely."""

    def __init__(self, config: H4D1ForwardOutcomeInterpretationReviewConfig) -> None:
        self.config = config

    def load_forward_outcomes(self) -> pd.DataFrame:
        return self._read("h4_transition_forward_outcomes")

    def load_outcome_profiles(self) -> pd.DataFrame:
        return self._read("h4_d1_forward_outcome_profiles")

    def load_dispersion_review(self) -> pd.DataFrame:
        return self._read("h4_d1_forward_outcome_dispersion_review")

    def load_sample_adequacy_review(self) -> pd.DataFrame:
        return self._read("h4_d1_forward_outcome_sample_adequacy_review")

    def load_aligned_summary(self) -> pd.DataFrame:
        return self._read("h4_d1_aligned_forward_outcome_research_summary")

    def load_contextual_profiles(self) -> pd.DataFrame:
        return self._read("h4_d1_same_time_contextual_transition_profiles")

    def load_contextual_sample_adequacy(self) -> pd.DataFrame:
        return self._read("h4_d1_context_sample_adequacy_review")

    def load_contextual_summary(self) -> pd.DataFrame:
        return self._read("h4_d1_same_time_contextual_transition_review_summary")

    def _read(self, source_name: str) -> pd.DataFrame:
        return read_optional_csv(expected_input_paths(self.config)[source_name])


def read_optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
