"""Source inventory for H4/D1 aligned forward outcome research."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_aligned_forward_outcome_research.loader import expected_input_paths, read_optional_csv
from sqre.h4_d1_aligned_forward_outcome_research.models import SourceInventoryRow


REQUIRED_SOURCES = {
    "h4_transition_d1_same_time_alignment",
    "h4_state_d1_same_time_alignment",
    "h4_d1_same_time_alignment_summary",
    "h4_normalized_ohlc",
    "d1_from_h4_ohlc",
    "h4_d1_candle_alignment_map",
    "h4_d1_synchronized_data_summary",
}


def build_source_inventory(
    same_time_alignment_dir: Path,
    synchronized_data_dir: Path,
    contextual_transition_dir: Path,
) -> list[SourceInventoryRow]:
    rows = []
    for name, path in expected_input_paths(same_time_alignment_dir, synchronized_data_dir, contextual_transition_dir).items():
        source_type = "REQUIRED_INPUT" if name in REQUIRED_SOURCES else "OPTIONAL_CONTEXTUAL_DIAGNOSTIC"
        rows.append(_source_row(name, source_type, path))
    return rows


def _source_row(name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    frame = read_optional_csv(path)
    if frame.empty:
        return SourceInventoryRow(name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
