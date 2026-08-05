"""Source inventory for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.loader import (
    QUERY_INTERFACE_INPUTS,
    REFERENCE_STORE_INPUTS,
    SNAPSHOT_INPUTS,
    ResearchDashboardPrototypeLoader,
)
from sqre.research_dashboard_prototype.models import DashboardSourceInventoryRow


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]


def build_source_inventory(config: ResearchDashboardPrototypeConfig) -> list[DashboardSourceInventoryRow]:
    rows: list[DashboardSourceInventoryRow] = []
    rows.extend(_group(config.snapshot_research_dir, SNAPSHOT_INPUTS, "REQUIRED_SNAPSHOT_RESEARCH_INPUT"))
    rows.extend(_group(config.query_interface_dir, QUERY_INTERFACE_INPUTS, "OPTIONAL_QUERY_INTERFACE_INPUT"))
    rows.extend(_group(config.reference_store_dir, REFERENCE_STORE_INPUTS, "OPTIONAL_REFERENCE_STORE_INPUT"))
    return rows


def has_missing_required_inputs(rows: list[DashboardSourceInventoryRow]) -> bool:
    return any(row.source_type.startswith("REQUIRED") and row.load_status == "REQUIRED_INPUT_MISSING" for row in rows)


def _group(directory: Path, filenames: dict[str, str], source_type: str) -> list[DashboardSourceInventoryRow]:
    rows = []
    for source_name, filename in filenames.items():
        path = directory / filename
        exists = path.exists()
        frame = ResearchDashboardPrototypeLoader.load_frame(path)
        status, diagnostic = _status(exists, frame, source_type)
        rows.append(
            DashboardSourceInventoryRow(
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
        if source_type.startswith("REQUIRED"):
            return "REQUIRED_INPUT_MISSING", "Required dashboard source file is missing."
        return "OPTIONAL_INPUT_MISSING", "Optional dashboard source file is missing."
    if frame.empty:
        return "EMPTY_INPUT", "Source file exists but has no data rows."
    return "LOADED", f"Loaded {len(frame)} rows."
