"""Load inputs for SQRE reference stability documentation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig


REQUIRED_STABILITY_VALIDATION_INPUTS = {
    "reference_stability_source_inventory": "reference_stability_source_inventory.csv",
    "reference_population_review": "reference_population_review.csv",
    "reference_horizon_stability_review": "reference_horizon_stability_review.csv",
    "reference_granularity_stability_review": "reference_granularity_stability_review.csv",
    "reference_sample_adequacy_review": "reference_sample_adequacy_review.csv",
    "reference_dispersion_stability_review": "reference_dispersion_stability_review.csv",
    "reference_directional_consistency_review": "reference_directional_consistency_review.csv",
    "reference_match_level_stability_review": "reference_match_level_stability_review.csv",
    "dashboard_reference_stability_review": "dashboard_reference_stability_review.csv",
    "reference_stability_scorecard": "reference_stability_scorecard.csv",
    "reference_stability_validation_summary": "reference_stability_validation_summary.csv",
}

REQUIRED_STABILITY_VALIDATION_TEXTS = {
    "reference_stability_validation_report": "reference_stability_validation_report.txt",
}

OPTIONAL_DASHBOARD_INPUTS = {
    "research_dashboard_summary": "research_dashboard_summary.csv",
    "research_dashboard_reference_cards": "research_dashboard_reference_cards.csv",
}

OPTIONAL_DASHBOARD_TEXTS = {
    "research_dashboard_prototype_report": "research_dashboard_prototype_report.txt",
    "research_dashboard_prototype_html": "research_dashboard_prototype.html",
}

OPTIONAL_MANUAL_DASHBOARD_INPUTS = {
    "manual_research_dashboard_review_summary": "manual_research_dashboard_review_summary.csv",
    "manual_research_dashboard_refinement_recommendations": "manual_research_dashboard_refinement_recommendations.csv",
}

OPTIONAL_MANUAL_DASHBOARD_TEXTS = {
    "manual_research_dashboard_review_report": "manual_research_dashboard_review_report.txt",
    "manual_research_dashboard_refined_html": "manual_research_dashboard_refined.html",
}


class ReferenceStabilityDocumentationLoader:
    """Read required and optional documentation inputs safely."""

    def __init__(self, config: ReferenceStabilityDocumentationConfig) -> None:
        self.config = config

    def load_frames(self) -> dict[str, pd.DataFrame]:
        frames: dict[str, pd.DataFrame] = {}
        frames.update(self._load_group(self.config.stability_validation_dir, REQUIRED_STABILITY_VALIDATION_INPUTS))
        frames.update(self._load_group(self.config.dashboard_dir, OPTIONAL_DASHBOARD_INPUTS))
        frames.update(self._load_group(self.config.manual_dashboard_review_dir, OPTIONAL_MANUAL_DASHBOARD_INPUTS))
        return frames

    def load_texts(self) -> dict[str, str]:
        texts: dict[str, str] = {}
        texts.update(self._load_text_group(self.config.stability_validation_dir, REQUIRED_STABILITY_VALIDATION_TEXTS))
        texts.update(self._load_text_group(self.config.dashboard_dir, OPTIONAL_DASHBOARD_TEXTS))
        texts.update(self._load_text_group(self.config.manual_dashboard_review_dir, OPTIONAL_MANUAL_DASHBOARD_TEXTS))
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
