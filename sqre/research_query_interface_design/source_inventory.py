"""Build source inventory for Research Query Interface Design."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.loader import (
    ALIGNMENT_INPUTS,
    INTERPRETATION_INPUTS,
    REFERENCE_STORE_INPUTS,
    USAGE_REVIEW_INPUTS,
)
from sqre.research_query_interface_design.models import SourceInventoryRow


def build_source_inventory(config: ResearchQueryInterfaceDesignConfig) -> list[SourceInventoryRow]:
    rows: list[SourceInventoryRow] = []
    rows.extend(_rows(config.reference_store_dir, REFERENCE_STORE_INPUTS, "REQUIRED_REFERENCE_STORE_INPUT"))
    rows.extend(_rows(config.usage_review_dir, USAGE_REVIEW_INPUTS, "REQUIRED_USAGE_REVIEW_INPUT"))
    rows.extend(_rows(config.interpretation_dir, INTERPRETATION_INPUTS, "OPTIONAL_DIAGNOSTIC_INPUT"))
    rows.extend(_rows(config.same_time_alignment_dir, ALIGNMENT_INPUTS, "OPTIONAL_SCENARIO_INPUT"))
    return rows


def _rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[SourceInventoryRow]:
    records = []
    for source_name, filename in filenames.items():
        path = directory / filename
        exists = path.exists()
        rows_loaded = _row_count(path) if exists else 0
        status = "LOADED" if exists else ("MISSING_REQUIRED" if source_type.startswith("REQUIRED") else "MISSING_OPTIONAL")
        diagnostic = f"Loaded {rows_loaded} rows." if exists else f"{filename} was not found."
        records.append(
            SourceInventoryRow(
                source_name=source_name,
                source_type=source_type,
                path=str(path),
                exists=exists,
                load_status=status,
                rows_loaded=rows_loaded,
                diagnostic=diagnostic,
            )
        )
    return records


def _row_count(path: Path) -> int:
    try:
        return len(pd.read_csv(path))
    except (pd.errors.EmptyDataError, OSError, ValueError):
        return 0

