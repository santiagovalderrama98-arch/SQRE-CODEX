"""Source inventory for H4/D1 same-time contextual transition review."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_same_time_contextual_transition_review.loader import expected_input_paths, read_optional_csv
from sqre.h4_d1_same_time_contextual_transition_review.models import SourceInventoryRow


REQUIRED_SOURCES = {
    "h4_transition_d1_same_time_alignment",
    "h4_state_d1_same_time_alignment",
    "h4_d1_same_time_alignment_coverage_review",
    "h4_d1_same_time_alignment_summary",
}


def build_source_inventory(same_time_alignment_dir: Path, timestamped_state_regime_dir: Path) -> list[SourceInventoryRow]:
    rows: list[SourceInventoryRow] = []
    for name, path in expected_input_paths(same_time_alignment_dir, timestamped_state_regime_dir).items():
        source_type = "SAME_TIME_ALIGNMENT_INPUT" if name in REQUIRED_SOURCES else "OPTIONAL_TIMESTAMPED_DIAGNOSTIC"
        rows.append(_source_row(name, source_type, path))
    return rows


def _source_row(name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    frame = read_optional_csv(path)
    if frame.empty:
        return SourceInventoryRow(name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
