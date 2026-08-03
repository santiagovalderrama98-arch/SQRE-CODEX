"""Resolve local H4 historical OHLC sources."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.loader import read_optional_csv
from sqre.h4_d1_synchronized_data_preparation.models import SourceInventoryRow


def resolve_h4_source(config: H4D1SynchronizedDataPreparationConfig) -> Path:
    if config.h4_input.exists():
        return config.h4_input
    for candidate in _candidate_paths(config):
        if candidate.exists():
            return candidate
    return config.h4_input


def build_source_inventory(config: H4D1SynchronizedDataPreparationConfig, resolved_h4_source: Path) -> list[SourceInventoryRow]:
    rows = [
        _source_row("requested_h4_input", "H4_LOCAL_INPUT", config.h4_input),
        _source_row("resolved_h4_input", "H4_LOCAL_INPUT", resolved_h4_source),
        _source_row("validation_config", "VALIDATION_CONFIG", config.validation_config),
        _source_row("validation_summary", "VALIDATION_SUMMARY", config.validation_summary),
    ]
    if config.allow_download:
        rows.append(
            SourceInventoryRow(
                source_name="optional_download",
                source_type="OPTIONAL_DOWNLOAD",
                path=config.provider or "",
                exists=False,
                load_status="SKIPPED_DOWNLOAD_NOT_IMPLEMENTED",
                rows_loaded=0,
                diagnostic="Optional download was requested, but this phase uses local data preparation only.",
            )
        )
    return rows


def _candidate_paths(config: H4D1SynchronizedDataPreparationConfig) -> list[Path]:
    candidates = sorted(Path("data/raw").glob(f"{config.symbol}_H4_*.csv"))
    candidates.extend(sorted(Path("data/raw/partial").glob(f"{config.symbol}_H4_*.csv")))
    return candidates


def _source_row(source_name: str, source_type: str, path: Path) -> SourceInventoryRow:
    if not path.exists():
        return SourceInventoryRow(source_name, source_type, str(path), False, "MISSING", 0, "Source file was not found.")
    if path.suffix.lower() not in {".csv", ".txt"}:
        return SourceInventoryRow(source_name, source_type, str(path), True, "AVAILABLE_NON_CSV", 0, "Source file exists and is not tabular input.")
    frame = read_optional_csv(path)
    if frame.empty:
        return SourceInventoryRow(source_name, source_type, str(path), True, "EMPTY", 0, "Source file has no data rows.")
    return SourceInventoryRow(source_name, source_type, str(path), True, "LOADED", len(frame), "Source file loaded.")
