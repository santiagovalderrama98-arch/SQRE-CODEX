"""Load local research outputs for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig


SNAPSHOT_INPUTS = {
    "snapshot_source_inventory": "current_market_state_snapshot_source_inventory.csv",
    "snapshot_context": "current_market_state_snapshot_context.csv",
    "snapshot_query_requests": "current_market_state_snapshot_query_requests.csv",
    "snapshot_reference_results": "current_market_state_snapshot_reference_results.csv",
    "snapshot_fallback_trace": "current_market_state_snapshot_fallback_trace.csv",
    "snapshot_evidence_review": "current_market_state_snapshot_evidence_review.csv",
    "snapshot_behavior_summary": "current_market_state_snapshot_behavior_summary.csv",
    "snapshot_diagnostic_review": "current_market_state_snapshot_diagnostic_review.csv",
    "snapshot_research_summary": "current_market_state_snapshot_research_summary.csv",
}
QUERY_INTERFACE_INPUTS = {
    "query_interface_summary": "research_query_interface_design_summary.csv",
    "query_results": "research_query_results.csv",
    "query_coverage_review": "research_query_coverage_review.csv",
    "query_result_quality_review": "research_query_result_quality_review.csv",
}
REFERENCE_STORE_INPUTS = {
    "reference_store_summary": "research_reference_store_design_summary.csv",
    "reference_store": "research_reference_store.csv",
    "reference_granularity_review": "research_reference_granularity_review.csv",
    "reference_horizon_review": "research_reference_horizon_review.csv",
}


class ResearchDashboardPrototypeLoader:
    """Read CSV inputs without failing on missing optional files."""

    def __init__(self, config: ResearchDashboardPrototypeConfig) -> None:
        self.config = config

    def load_inputs(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.snapshot_research_dir, SNAPSHOT_INPUTS))
        frames.update(self._load_group(self.config.query_interface_dir, QUERY_INTERFACE_INPUTS))
        frames.update(self._load_group(self.config.reference_store_dir, REFERENCE_STORE_INPUTS))
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
