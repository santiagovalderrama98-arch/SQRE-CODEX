"""Source inventory for D1 regime context adequacy review."""

from __future__ import annotations

from pathlib import Path

from sqre.d1_regime_context_adequacy_review.loader import expected_input_paths, read_optional_csv
from sqre.d1_regime_context_adequacy_review.models import SourceInventoryRow


REQUIRED_SOURCES = {
    "h4_d1_same_time_contextual_transition_profiles",
    "h4_transition_d1_market_state_distribution",
    "h4_transition_d1_regime_distribution",
    "h4_transition_context_concentration_review",
    "h4_d1_context_sample_adequacy_review",
    "h4_d1_same_time_contextual_transition_review_summary",
}


def build_source_inventory(
    contextual_transition_dir: Path,
    same_time_alignment_dir: Path,
    timestamped_state_regime_dir: Path,
) -> list[SourceInventoryRow]:
    rows = []
    for name, path in expected_input_paths(
        contextual_transition_dir,
        same_time_alignment_dir,
        timestamped_state_regime_dir,
    ).items():
        source_type = "CONTEXTUAL_TRANSITION_INPUT" if name in REQUIRED_SOURCES else "OPTIONAL_SUPPORTING_DIAGNOSTIC"
        rows.append(_source_row(name, source_type, path))
    return rows


def _source_row(name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    frame = read_optional_csv(path)
    if frame.empty:
        return SourceInventoryRow(name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
