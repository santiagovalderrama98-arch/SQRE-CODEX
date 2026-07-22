"""Candidate selection for targeted H4 partial expansion validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.h4_targeted_partial_expansion_validation.config import H4TargetedPartialExpansionValidationConfig
from sqre.h4_targeted_partial_expansion_validation.loader import number_value, read_optional_csv, text_value
from sqre.h4_targeted_partial_expansion_validation.models import PartialCandidate


def load_partial_candidates(config: H4TargetedPartialExpansionValidationConfig) -> list[PartialCandidate]:
    candidates_path = config.feasibility_dir / "h4_feasible_expansion_candidates.csv"
    matrix_path = config.feasibility_dir / "h4_expansion_feasibility_matrix.csv"
    candidates_frame = read_optional_csv(candidates_path)
    frame = candidates_frame if not candidates_frame.empty else read_optional_csv(matrix_path)
    if frame.empty:
        return []

    availability = _availability_by_id(config.feasibility_dir / "h4_availability_review.csv")
    selected: list[PartialCandidate] = []
    for _, row in frame.iterrows():
        feasibility_class = text_value(row, ["Feasibility_Class", "feasibility_class"]).upper()
        candidate_id = text_value(row, ["Candidate_ID", "candidate_id", "Scenario_ID", "scenario_id"])
        timeframe = text_value(row, ["Timeframe", "timeframe"]).upper()
        if feasibility_class != "FEASIBLE_PARTIAL_SAMPLE" or timeframe != "H4":
            continue
        if config.candidate_id and candidate_id.lower() != config.candidate_id.lower():
            continue

        extra = availability.get(candidate_id.lower(), {})
        raw_path, raw_status = locate_raw_file(row, config, extra)
        diagnostic = "Selected partial H4 candidate for isolated review."
        if raw_status == "MISSING":
            diagnostic = "Selected candidate has no readable local raw file."
        elif raw_status == "UNREADABLE":
            diagnostic = "Selected candidate raw file is present but cannot be read."

        selected.append(
            PartialCandidate(
                candidate_id=candidate_id,
                symbol=text_value(row, ["Symbol", "symbol"], "EURUSD").upper(),
                timeframe=timeframe,
                sample_label=config.partial_sample_label,
                feasibility_class=feasibility_class,
                coverage_ratio=number_value(row, ["Coverage_Ratio", "coverage_ratio"]),
                raw_file_path=str(raw_path) if raw_path else "",
                raw_file_status=raw_status,
                defined_start_date=text_value(row, ["Defined_Start_Date", "defined_start_date"]),
                defined_end_date=text_value(row, ["Defined_End_Date", "defined_end_date"]),
                actual_start_date=str(extra.get("actual_start_date", "")),
                actual_end_date=str(extra.get("actual_end_date", "")),
                candidate_selection_status="SELECTED",
                candidate_diagnostic=diagnostic,
            )
        )
    return selected


def locate_raw_file(
    row: pd.Series,
    config: H4TargetedPartialExpansionValidationConfig,
    availability: dict[str, object] | None = None,
) -> tuple[Path | None, str]:
    availability = availability or {}
    hints = [
        text_value(row, ["Raw_File_Path", "raw_file_path"]),
        str(availability.get("raw_file_path", "")),
    ]
    for hint in hints:
        if not hint:
            continue
        path = Path(hint)
        if not path.is_absolute():
            path = Path.cwd() / path
        status = _path_status(path)
        if status == "FOUND":
            return path, status

    candidate_id = text_value(row, ["Candidate_ID", "candidate_id", "Scenario_ID", "scenario_id"])
    symbol = text_value(row, ["Symbol", "symbol"], "EURUSD").upper()
    timeframe = text_value(row, ["Timeframe", "timeframe"], "H4").upper()
    expected_name = f"{symbol}_{timeframe}_period_5_partial.csv"
    expected_paths = [
        config.partial_data_dir / expected_name,
        config.raw_data_dir / expected_name,
    ]
    for path in expected_paths:
        status = _path_status(path)
        if status == "FOUND":
            return path, status
        if status == "UNREADABLE":
            return path, status

    for directory in [config.partial_data_dir, config.raw_data_dir]:
        if not directory.exists():
            continue
        matches = sorted(directory.glob(f"{symbol}_{timeframe}*.csv"))
        preferred = [path for path in matches if candidate_id.lower() in path.stem.lower()]
        for path in preferred or matches:
            status = _path_status(path)
            if status == "FOUND":
                return path, status
            if status == "UNREADABLE":
                return path, status
    return None, "MISSING"


def _availability_by_id(path: Path) -> dict[str, dict[str, object]]:
    frame = read_optional_csv(path)
    output: dict[str, dict[str, object]] = {}
    if frame.empty:
        return output
    for _, row in frame.iterrows():
        scenario_id = text_value(row, ["Scenario_ID", "scenario_id"])
        if not scenario_id:
            continue
        output[scenario_id.lower()] = {
            "actual_start_date": text_value(row, ["Actual_Start_Date", "actual_start_date"]),
            "actual_end_date": text_value(row, ["Actual_End_Date", "actual_end_date"]),
            "raw_file_path": text_value(row, ["Raw_File_Path", "raw_file_path"]),
        }
    return output


def _path_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        with path.open("r", encoding="utf-8"):
            return "FOUND"
    except OSError:
        return "UNREADABLE"
