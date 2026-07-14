"""Dataclass models for master historical calibration summaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "Scenario_ID",
    "Status",
    "Symbol",
    "Timeframe",
    "OHLC_File",
    "Period_Start",
    "Period_End",
    "OHLC_Rows",
    "Structures_Detected",
    "Average_Structure_Duration",
    "Unique_States",
    "Most_Common_State",
    "Average_Forward_Range_Pips",
    "Direction_Alignment_Rate",
]


ADDED_COLUMNS = [
    "Source_File",
    "Source_Row_Index",
    "Duplicate_Count_For_Scenario",
    "Was_Duplicate",
    "Dedupe_Policy",
]


@dataclass(frozen=True)
class LoadedSummaryFrame:
    frame: pd.DataFrame
    requested_files: list[str] = field(default_factory=list)
    found_files: list[str] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)
    rows_loaded: int = 0


@dataclass(frozen=True)
class DuplicateScenarioDetail:
    scenario_id: str
    duplicate_count: int
    retained_source_file: str
    retained_source_row_index: int
    source_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DedupeResult:
    frame: pd.DataFrame
    rows_loaded: int
    rows_retained: int
    duplicate_scenario_ids: list[str] = field(default_factory=list)
    duplicate_details: list[DuplicateScenarioDetail] = field(default_factory=list)


@dataclass(frozen=True)
class MasterCalibrationSummaryResult:
    requested_files: list[str]
    found_files: list[str]
    missing_files: list[str]
    rows_loaded: int
    rows_retained: int
    duplicate_scenario_ids: list[str]
    duplicate_details: list[DuplicateScenarioDetail]
    timeframe_counts: dict[str, int]
    output_path: Path
    report_path: Path
    dedupe_key: str = "Scenario_ID"
    dedupe_policy: str = "last"
