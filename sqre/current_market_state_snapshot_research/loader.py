"""Load inputs for Current Market State Snapshot Research."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig


REFERENCE_STORE_INPUTS = {
    "reference_store": "research_reference_store.csv",
    "reference_candidates": "research_reference_candidates.csv",
    "reference_granularity_review": "research_reference_granularity_review.csv",
    "reference_horizon_review": "research_reference_horizon_review.csv",
    "reference_store_summary": "research_reference_store_design_summary.csv",
}
QUERY_INTERFACE_INPUTS = {
    "query_requests_input": "research_query_requests.csv",
    "query_results_input": "research_query_results.csv",
    "query_fallback_trace_input": "research_query_fallback_trace.csv",
    "query_evidence_quality_input": "research_query_evidence_quality_review.csv",
    "query_coverage_input": "research_query_coverage_review.csv",
    "query_result_quality_input": "research_query_result_quality_review.csv",
    "query_interface_summary": "research_query_interface_design_summary.csv",
}
USAGE_REVIEW_INPUTS = {
    "usage_lookup_results": "research_reference_lookup_results.csv",
    "usage_scenarios": "research_reference_usage_scenarios.csv",
    "usage_summary": "research_reference_store_usage_review_summary.csv",
}
SAME_TIME_ALIGNMENT_INPUTS = {
    "transition_alignment": "h4_transition_d1_same_time_alignment.csv",
    "state_alignment": "h4_state_d1_same_time_alignment.csv",
    "alignment_summary": "h4_d1_same_time_alignment_summary.csv",
}
TIMESTAMPED_INPUTS = {
    "h4_timestamped_states": "h4_timestamped_market_states.csv",
    "h4_timestamped_transitions": "h4_timestamped_transitions.csv",
    "d1_timestamped_states": "d1_timestamped_market_states.csv",
    "timestamped_summary": "h4_d1_timestamped_state_regime_summary.csv",
}


class CurrentMarketStateSnapshotResearchLoader:
    """Read CSV inputs without failing on optional missing files."""

    def __init__(self, config: CurrentMarketStateSnapshotResearchConfig) -> None:
        self.config = config

    def load_inputs(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.reference_store_dir, REFERENCE_STORE_INPUTS))
        frames.update(self._load_group(self.config.query_interface_dir, QUERY_INTERFACE_INPUTS))
        frames.update(self._load_group(self.config.usage_review_dir, USAGE_REVIEW_INPUTS))
        frames.update(self._load_group(self.config.same_time_alignment_dir, SAME_TIME_ALIGNMENT_INPUTS))
        frames.update(self._load_group(self.config.timestamped_state_regime_dir, TIMESTAMPED_INPUTS))
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
