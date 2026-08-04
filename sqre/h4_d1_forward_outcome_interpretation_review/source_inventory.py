"""Source inventory for H4/D1 forward outcome interpretation review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_d1_forward_outcome_interpretation_review.config import (
    H4D1ForwardOutcomeInterpretationReviewConfig,
)
from sqre.h4_d1_forward_outcome_interpretation_review.models import SourceInventoryRow


REQUIRED_SOURCES = {
    "h4_transition_forward_outcomes": "h4_transition_forward_outcomes.csv",
    "h4_d1_forward_outcome_profiles": "h4_d1_forward_outcome_profiles.csv",
    "h4_d1_forward_outcome_dispersion_review": "h4_d1_forward_outcome_dispersion_review.csv",
    "h4_d1_forward_outcome_sample_adequacy_review": "h4_d1_forward_outcome_sample_adequacy_review.csv",
    "h4_d1_aligned_forward_outcome_research_summary": "h4_d1_aligned_forward_outcome_research_summary.csv",
}

OPTIONAL_SOURCES = {
    "h4_d1_same_time_contextual_transition_profiles": "h4_d1_same_time_contextual_transition_profiles.csv",
    "h4_d1_context_sample_adequacy_review": "h4_d1_context_sample_adequacy_review.csv",
    "h4_d1_same_time_contextual_transition_review_summary": "h4_d1_same_time_contextual_transition_review_summary.csv",
}


def build_source_inventory(config: H4D1ForwardOutcomeInterpretationReviewConfig) -> list[SourceInventoryRow]:
    rows: list[SourceInventoryRow] = []
    for name, filename in REQUIRED_SOURCES.items():
        rows.append(_inventory_row(name, "REQUIRED_INPUT", config.forward_outcome_dir / filename))
    for name, filename in OPTIONAL_SOURCES.items():
        rows.append(_inventory_row(name, "OPTIONAL_CONTEXTUAL_DIAGNOSTIC", config.contextual_transition_dir / filename))
    return rows


def expected_input_paths(config: H4D1ForwardOutcomeInterpretationReviewConfig) -> dict[str, Path]:
    paths = {name: config.forward_outcome_dir / filename for name, filename in REQUIRED_SOURCES.items()}
    paths.update({name: config.contextual_transition_dir / filename for name, filename in OPTIONAL_SOURCES.items()})
    return paths


def _inventory_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "Source file is missing.")
    try:
        frame = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        return SourceInventoryRow(source_name, source_type, str(path), True, "ERROR", 0, f"Source file could not load: {exc}")
    if frame.empty:
        return SourceInventoryRow(source_name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(source_name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
