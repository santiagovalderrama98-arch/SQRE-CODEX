"""Load inputs for SQRE reference stability validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.reference_stability_validation.config import ReferenceStabilityValidationConfig


REQUIRED_REFERENCE_STORE_INPUTS = {
    "reference_store": "research_reference_store.csv",
    "reference_candidates": "research_reference_candidates.csv",
    "reference_exclusion_review": "research_reference_exclusion_review.csv",
    "reference_granularity_review": "research_reference_granularity_review.csv",
    "reference_horizon_review": "research_reference_horizon_review.csv",
    "reference_store_summary": "research_reference_store_design_summary.csv",
}

REQUIRED_QUERY_INTERFACE_INPUTS = {
    "query_requests": "research_query_requests.csv",
    "query_results": "research_query_results.csv",
    "query_fallback_trace": "research_query_fallback_trace.csv",
    "query_evidence_quality_review": "research_query_evidence_quality_review.csv",
    "query_coverage_review": "research_query_coverage_review.csv",
    "query_result_quality_review": "research_query_result_quality_review.csv",
    "query_interface_summary": "research_query_interface_design_summary.csv",
}

OPTIONAL_SNAPSHOT_INPUTS = {
    "snapshot_context": "current_market_state_snapshot_context.csv",
    "snapshot_reference_results": "current_market_state_snapshot_reference_results.csv",
    "snapshot_behavior_summary": "current_market_state_snapshot_behavior_summary.csv",
    "snapshot_research_summary": "current_market_state_snapshot_research_summary.csv",
}

OPTIONAL_DASHBOARD_INPUTS = {
    "dashboard_reference_cards": "research_dashboard_reference_cards.csv",
    "dashboard_summary": "research_dashboard_summary.csv",
    "dashboard_behavior_panel": "research_dashboard_behavior_panel.csv",
    "dashboard_evidence_panel": "research_dashboard_evidence_panel.csv",
}

OPTIONAL_MANUAL_REVIEW_INPUTS = {
    "manual_dashboard_review_summary": "manual_research_dashboard_review_summary.csv",
    "manual_dashboard_refinement_recommendations": "manual_research_dashboard_refinement_recommendations.csv",
}


class ReferenceStabilityValidationLoader:
    """Read required and optional phase inputs safely."""

    def __init__(self, config: ReferenceStabilityValidationConfig) -> None:
        self.config = config

    def load_frames(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.reference_store_dir, REQUIRED_REFERENCE_STORE_INPUTS))
        frames.update(self._load_group(self.config.query_interface_dir, REQUIRED_QUERY_INTERFACE_INPUTS))
        frames.update(self._load_group(self.config.snapshot_research_dir, OPTIONAL_SNAPSHOT_INPUTS))
        frames.update(self._load_group(self.config.dashboard_dir, OPTIONAL_DASHBOARD_INPUTS))
        frames.update(self._load_group(self.config.manual_dashboard_review_dir, OPTIONAL_MANUAL_REVIEW_INPUTS))
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
