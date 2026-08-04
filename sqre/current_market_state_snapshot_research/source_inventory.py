"""Source inventory for Current Market State Snapshot Research."""

from __future__ import annotations

import pandas as pd

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.loader import (
    QUERY_INTERFACE_INPUTS,
    REFERENCE_STORE_INPUTS,
    SAME_TIME_ALIGNMENT_INPUTS,
    TIMESTAMPED_INPUTS,
    USAGE_REVIEW_INPUTS,
    CurrentMarketStateSnapshotResearchLoader,
)
from sqre.current_market_state_snapshot_research.models import SourceInventoryRow


def build_source_inventory(config: CurrentMarketStateSnapshotResearchConfig) -> list[SourceInventoryRow]:
    rows: list[SourceInventoryRow] = []
    rows.extend(_group(config.reference_store_dir, REFERENCE_STORE_INPUTS, "REQUIRED_REFERENCE_STORE_INPUT"))
    rows.extend(_group(config.query_interface_dir, QUERY_INTERFACE_INPUTS, "REQUIRED_QUERY_INTERFACE_INPUT"))
    rows.extend(_group(config.usage_review_dir, USAGE_REVIEW_INPUTS, "OPTIONAL_USAGE_REVIEW_INPUT"))
    rows.extend(_group(config.same_time_alignment_dir, SAME_TIME_ALIGNMENT_INPUTS, "OPTIONAL_SAME_TIME_ALIGNMENT_INPUT"))
    rows.extend(_group(config.timestamped_state_regime_dir, TIMESTAMPED_INPUTS, "OPTIONAL_TIMESTAMPED_STATE_REGIME_INPUT"))
    return rows


def _group(directory, filenames: dict[str, str], source_type: str) -> list[SourceInventoryRow]:
    rows = []
    for source_name, filename in filenames.items():
        path = directory / filename
        exists = path.exists()
        frame = CurrentMarketStateSnapshotResearchLoader.load_frame(path)
        status, diagnostic = _status(exists, frame, source_type)
        rows.append(
            SourceInventoryRow(
                source_name=source_name,
                source_type=source_type,
                path=str(path),
                exists=exists,
                load_status=status,
                rows_loaded=len(frame),
                diagnostic=diagnostic,
            )
        )
    return rows


def _status(exists: bool, frame: pd.DataFrame, source_type: str) -> tuple[str, str]:
    if not exists:
        required = source_type.startswith("REQUIRED")
        return ("INPUT_MISSING", "Required source file is missing." if required else "Optional source file is missing.")
    if frame.empty:
        return "LOADED_EMPTY", "Source file exists but has no data rows."
    return "LOADED", f"Loaded {len(frame)} rows."
