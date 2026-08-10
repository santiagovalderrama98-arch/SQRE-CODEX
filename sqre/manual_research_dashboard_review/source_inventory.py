"""Source inventory for manual research dashboard review."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.loader import (
    DASHBOARD_CSV_INPUTS,
    DASHBOARD_TEXT_INPUTS,
    OPTIONAL_QUERY_INPUTS,
    OPTIONAL_SNAPSHOT_INPUTS,
)
from sqre.manual_research_dashboard_review.models import ReviewSourceInventoryRow


SOURCE_COLUMNS = ["Source_Name", "Source_Type", "Path", "Exists", "Load_Status", "Rows_Loaded", "Diagnostic"]


def build_source_inventory(config: ManualResearchDashboardReviewConfig) -> list[ReviewSourceInventoryRow]:
    rows: list[ReviewSourceInventoryRow] = []
    rows.extend(_csv_rows(config.dashboard_dir, DASHBOARD_CSV_INPUTS, "REQUIRED_DASHBOARD_SOURCE"))
    rows.extend(_text_rows(config.dashboard_dir, DASHBOARD_TEXT_INPUTS, "REQUIRED_DASHBOARD_SOURCE"))
    rows.extend(_csv_rows(config.snapshot_research_dir, OPTIONAL_SNAPSHOT_INPUTS, "OPTIONAL_SNAPSHOT_SOURCE"))
    rows.extend(_csv_rows(config.query_interface_dir, OPTIONAL_QUERY_INPUTS, "OPTIONAL_QUERY_SOURCE"))
    return rows


def has_missing_required_inputs(rows: list[ReviewSourceInventoryRow]) -> bool:
    return any(
        row.source_type == "REQUIRED_DASHBOARD_SOURCE"
        and row.load_status in {"REQUIRED_INPUT_MISSING", "INPUT_MISSING"}
        for row in rows
    )


def _csv_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[ReviewSourceInventoryRow]:
    return [_csv_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _text_rows(directory: Path, filenames: dict[str, str], source_type: str) -> list[ReviewSourceInventoryRow]:
    return [_text_row(name, source_type, directory / filename) for name, filename in filenames.items()]


def _csv_row(source_name: str, source_type: str, path: Path) -> ReviewSourceInventoryRow:
    if not path.exists():
        status = "REQUIRED_INPUT_MISSING" if source_type == "REQUIRED_DASHBOARD_SOURCE" else "OPTIONAL_INPUT_MISSING"
        return ReviewSourceInventoryRow(source_name, source_type, str(path), False, status, 0, f"{path.name} is missing.")
    try:
        rows_loaded = len(pd.read_csv(path))
    except pd.errors.EmptyDataError:
        return ReviewSourceInventoryRow(source_name, source_type, str(path), True, "EMPTY_INPUT", 0, f"{path.name} is empty.")
    status = "LOADED" if rows_loaded > 0 else "EMPTY_INPUT"
    diagnostic = f"{path.name} loaded." if status == "LOADED" else f"{path.name} has no data rows."
    return ReviewSourceInventoryRow(source_name, source_type, str(path), True, status, rows_loaded, diagnostic)


def _text_row(source_name: str, source_type: str, path: Path) -> ReviewSourceInventoryRow:
    if not path.exists():
        return ReviewSourceInventoryRow(
            source_name,
            source_type,
            str(path),
            False,
            "REQUIRED_INPUT_MISSING",
            0,
            f"{path.name} is missing.",
        )
    text = path.read_text(encoding="utf-8")
    status = "LOADED" if text.strip() else "EMPTY_INPUT"
    rows_loaded = 1 if text.strip() else 0
    diagnostic = f"{path.name} loaded." if rows_loaded else f"{path.name} is empty."
    return ReviewSourceInventoryRow(source_name, source_type, str(path), True, status, rows_loaded, diagnostic)
