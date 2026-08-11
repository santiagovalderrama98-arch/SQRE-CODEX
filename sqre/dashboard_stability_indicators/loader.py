"""Load inputs for SQRE dashboard stability indicators."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig


REQUIRED_DOCUMENTATION_INPUTS = {
    "documentation_source_inventory": "reference_stability_documentation_source_inventory.csv",
    "interpretation_guide": "reference_stability_interpretation_guide.csv",
    "evidence_usage_policy": "reference_evidence_usage_policy.csv",
    "dashboard_reading_guide": "reference_dashboard_reading_guide.csv",
    "limitations_documentation": "reference_stability_limitations_documentation.csv",
    "follow_up_plan": "reference_stability_follow_up_plan.csv",
    "documentation_scope_safety_review": "reference_stability_documentation_scope_safety_review.csv",
    "documentation_summary": "reference_stability_documentation_summary.csv",
}

REQUIRED_DOCUMENTATION_TEXTS = {
    "documentation_report": "reference_stability_documentation_report.txt",
    "documentation_markdown": "reference_stability_documentation.md",
}

REQUIRED_VALIDATION_INPUTS = {
    "reference_population_review": "reference_population_review.csv",
    "horizon_stability_review": "reference_horizon_stability_review.csv",
    "granularity_stability_review": "reference_granularity_stability_review.csv",
    "sample_adequacy_review": "reference_sample_adequacy_review.csv",
    "dispersion_stability_review": "reference_dispersion_stability_review.csv",
    "directional_consistency_review": "reference_directional_consistency_review.csv",
    "match_level_stability_review": "reference_match_level_stability_review.csv",
    "dashboard_reference_stability_review": "dashboard_reference_stability_review.csv",
    "reference_stability_scorecard": "reference_stability_scorecard.csv",
    "reference_stability_validation_summary": "reference_stability_validation_summary.csv",
}

REQUIRED_DASHBOARD_INPUTS = {
    "dashboard_summary": "research_dashboard_summary.csv",
    "snapshot_panel": "research_dashboard_snapshot_panel.csv",
    "reference_cards": "research_dashboard_reference_cards.csv",
    "evidence_panel": "research_dashboard_evidence_panel.csv",
    "behavior_panel": "research_dashboard_behavior_panel.csv",
    "fallback_panel": "research_dashboard_fallback_panel.csv",
    "diagnostic_panel": "research_dashboard_diagnostic_panel.csv",
}

REQUIRED_DASHBOARD_TEXTS = {
    "dashboard_report": "research_dashboard_prototype_report.txt",
    "dashboard_html": "research_dashboard_prototype.html",
}

OPTIONAL_MANUAL_REVIEW_INPUTS = {
    "manual_review_summary": "manual_research_dashboard_review_summary.csv",
    "manual_refinement_recommendations": "manual_research_dashboard_refinement_recommendations.csv",
}

OPTIONAL_MANUAL_REVIEW_TEXTS = {
    "manual_refined_html": "manual_research_dashboard_refined.html",
}


class DashboardStabilityIndicatorsLoader:
    """Read required and optional phase inputs safely."""

    def __init__(self, config: DashboardStabilityIndicatorsConfig) -> None:
        self.config = config

    def load_frames(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.stability_documentation_dir, REQUIRED_DOCUMENTATION_INPUTS))
        frames.update(self._load_group(self.config.stability_validation_dir, REQUIRED_VALIDATION_INPUTS))
        frames.update(self._load_group(self.config.dashboard_dir, REQUIRED_DASHBOARD_INPUTS))
        frames.update(self._load_group(self.config.manual_dashboard_review_dir, OPTIONAL_MANUAL_REVIEW_INPUTS))
        return frames

    def load_texts(self) -> dict[str, str]:
        texts: dict[str, str] = {}
        texts.update(self._load_text_group(self.config.stability_documentation_dir, REQUIRED_DOCUMENTATION_TEXTS))
        texts.update(self._load_text_group(self.config.dashboard_dir, REQUIRED_DASHBOARD_TEXTS))
        texts.update(self._load_text_group(self.config.manual_dashboard_review_dir, OPTIONAL_MANUAL_REVIEW_TEXTS))
        return texts

    def _load_group(self, directory: Path, filenames: dict[str, str]) -> dict[str, pd.DataFrame]:
        return {name: self.load_frame(directory / filename) for name, filename in filenames.items()}

    def _load_text_group(self, directory: Path, filenames: dict[str, str]) -> dict[str, str]:
        return {name: self.load_text(directory / filename) for name, filename in filenames.items()}

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
