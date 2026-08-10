"""Load dashboard prototype outputs for manual usability review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig


DASHBOARD_CSV_INPUTS = {
    "prototype_source_inventory": "research_dashboard_source_inventory.csv",
    "prototype_snapshot_panel": "research_dashboard_snapshot_panel.csv",
    "prototype_reference_cards": "research_dashboard_reference_cards.csv",
    "prototype_evidence_panel": "research_dashboard_evidence_panel.csv",
    "prototype_behavior_panel": "research_dashboard_behavior_panel.csv",
    "prototype_fallback_panel": "research_dashboard_fallback_panel.csv",
    "prototype_diagnostic_panel": "research_dashboard_diagnostic_panel.csv",
    "prototype_summary": "research_dashboard_summary.csv",
}

DASHBOARD_TEXT_INPUTS = {
    "prototype_report": "research_dashboard_prototype_report.txt",
    "prototype_html": "research_dashboard_prototype.html",
}

OPTIONAL_SNAPSHOT_INPUTS = {
    "snapshot_context": "current_market_state_snapshot_context.csv",
    "snapshot_reference_results": "current_market_state_snapshot_reference_results.csv",
    "snapshot_behavior_summary": "current_market_state_snapshot_behavior_summary.csv",
    "snapshot_research_summary": "current_market_state_snapshot_research_summary.csv",
}

OPTIONAL_QUERY_INPUTS = {
    "query_interface_summary": "research_query_interface_design_summary.csv",
    "query_results": "research_query_results.csv",
    "query_coverage_review": "research_query_coverage_review.csv",
    "query_result_quality_review": "research_query_result_quality_review.csv",
}


class ManualResearchDashboardReviewLoader:
    """Read required and optional dashboard review inputs safely."""

    def __init__(self, config: ManualResearchDashboardReviewConfig) -> None:
        self.config = config

    def load_frames(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.dashboard_dir, DASHBOARD_CSV_INPUTS))
        frames.update(self._load_group(self.config.snapshot_research_dir, OPTIONAL_SNAPSHOT_INPUTS))
        frames.update(self._load_group(self.config.query_interface_dir, OPTIONAL_QUERY_INPUTS))
        return frames

    def load_texts(self) -> dict[str, str]:
        return {
            name: self.load_text(self.config.dashboard_dir / filename)
            for name, filename in DASHBOARD_TEXT_INPUTS.items()
        }

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

    @staticmethod
    def load_text(path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")
