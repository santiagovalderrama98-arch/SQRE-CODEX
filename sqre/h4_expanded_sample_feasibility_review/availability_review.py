"""Availability review for H4 sample feasibility."""

from __future__ import annotations

import pandas as pd

from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.loader import number_value, text_value
from sqre.h4_expanded_sample_feasibility_review.models import (
    AvailabilityReviewRow,
    DefinedSampleRow,
    RawFileInventoryRow,
)
from sqre.h4_expanded_sample_feasibility_review.raw_file_inspector import scenario_id_from_raw_file


def build_availability_review(
    defined_samples: list[DefinedSampleRow],
    availability_frame: pd.DataFrame,
    raw_files: list[RawFileInventoryRow],
    config: H4ExpandedSampleFeasibilityConfig,
) -> list[AvailabilityReviewRow]:
    definitions = {row.scenario_id: row for row in defined_samples}
    raw_by_scenario = _raw_by_scenario(raw_files)
    availability_records = _availability_records(availability_frame)
    scenario_ids = sorted(set(definitions) | set(raw_by_scenario) | set(availability_records))

    rows: list[AvailabilityReviewRow] = []
    for scenario_id in scenario_ids:
        defined = definitions.get(scenario_id)
        record = availability_records.get(scenario_id, {})
        raw = _matching_raw(scenario_id, defined, raw_by_scenario)
        coverage_ratio = _coverage_ratio(record, raw)
        explicit_status = str(record.get("availability_status", "")).upper()
        availability_status = classify_availability_status(explicit_status, coverage_ratio, raw, config)
        rows.append(
            AvailabilityReviewRow(
                scenario_id=scenario_id,
                symbol=str(record.get("symbol") or (defined.symbol if defined else "EURUSD")),
                timeframe="H4",
                defined_start_date=str(record.get("expected_start") or (defined.defined_start_date if defined else "")),
                defined_end_date=str(record.get("expected_end") or (defined.defined_end_date if defined else "")),
                availability_status=availability_status,
                coverage_ratio=coverage_ratio,
                actual_start_date=str(record.get("actual_start") or (raw.first_date if raw else "")),
                actual_end_date=str(record.get("actual_end") or (raw.last_date if raw else "")),
                raw_file_path=raw.file_path if raw else "",
                partial_file_flag=raw.partial_file_flag if raw else "NO",
                availability_diagnostic=availability_diagnostic(availability_status),
            )
        )
    return rows


def classify_availability_status(
    explicit_status: str,
    coverage_ratio: float,
    raw: RawFileInventoryRow | None,
    config: H4ExpandedSampleFeasibilityConfig,
) -> str:
    explicit_status = explicit_status.upper()
    if "MISSING" in explicit_status or "UNAVAILABLE" in explicit_status:
        return "MISSING"
    if coverage_ratio >= config.minimum_full_coverage_ratio:
        return "AVAILABLE_FULL"
    if config.minimum_partial_coverage_ratio <= coverage_ratio < config.minimum_full_coverage_ratio:
        return "AVAILABLE_PARTIAL"
    if raw is not None and raw.date_coverage_status == "KNOWN" and raw.row_count > 0:
        return "AVAILABLE_PARTIAL"
    if raw is None and not explicit_status:
        return "MISSING"
    return "UNKNOWN"


def availability_diagnostic(availability_status: str) -> str:
    return {
        "AVAILABLE_FULL": "H4 sample appears to have full local coverage",
        "AVAILABLE_PARTIAL": "H4 sample appears to have partial local coverage",
        "MISSING": "H4 sample is missing or unavailable in current local data",
        "UNKNOWN": "H4 sample availability cannot be determined from available diagnostics",
    }.get(availability_status, "H4 sample availability requires review")


def _availability_records(frame: pd.DataFrame) -> dict[str, dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    if frame.empty:
        return records
    for _, row in frame.iterrows():
        timeframe = text_value(row, "Timeframe", "timeframe").upper()
        if timeframe != "H4":
            continue
        scenario_id = text_value(row, "Scenario_ID", "scenario_id", "Scenario", "Sample_ID", "Name")
        if not scenario_id:
            continue
        records[scenario_id] = {
            "symbol": text_value(row, "Symbol", "symbol", default="EURUSD"),
            "expected_start": text_value(row, "Expected_Start", "Start_Date", "start_date"),
            "expected_end": text_value(row, "Expected_End", "End_Date", "end_date"),
            "actual_start": text_value(row, "Actual_Start", "Actual_Start_Date"),
            "actual_end": text_value(row, "Actual_End", "Actual_End_Date"),
            "coverage_ratio": number_value(row, "Coverage_Ratio", "Data_Coverage_Ratio", default=0.0),
            "availability_status": text_value(row, "Availability_Status", "Status"),
        }
    return records


def _raw_by_scenario(raw_files: list[RawFileInventoryRow]) -> dict[str, RawFileInventoryRow]:
    rows: dict[str, RawFileInventoryRow] = {}
    for row in raw_files:
        rows[scenario_id_from_raw_file(row)] = row
    return rows


def _matching_raw(
    scenario_id: str,
    defined: DefinedSampleRow | None,
    raw_by_scenario: dict[str, RawFileInventoryRow],
) -> RawFileInventoryRow | None:
    if defined and defined.raw_file_hint:
        for raw in raw_by_scenario.values():
            if raw.file_path == defined.raw_file_hint or raw.file_name == defined.raw_file_hint.split("/")[-1]:
                return raw
    return raw_by_scenario.get(scenario_id)


def _coverage_ratio(record: dict[str, object], raw: RawFileInventoryRow | None) -> float:
    if record and float(record.get("coverage_ratio") or 0.0) > 0:
        return float(record.get("coverage_ratio") or 0.0)
    if raw and raw.row_count > 0 and raw.date_coverage_status == "KNOWN":
        return 1.0 if raw.partial_file_flag == "NO" else 0.5
    return 0.0
