#!/usr/bin/env python3
"""Check data availability for SQRE expanded historical samples."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from generate_expanded_sample_download_commands import load_sample_config


EXPECTED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]
OUTPUT_COLUMNS = [
    "Sample_ID",
    "Scenario_ID",
    "Symbol",
    "Timeframe",
    "Expected_Start",
    "Expected_End",
    "Output_Path",
    "Exists",
    "Rows",
    "Valid_Columns",
    "First_Date",
    "Last_Date",
    "Expected_Duration_Days",
    "Actual_Coverage_Days",
    "Start_Gap_Days",
    "End_Gap_Days",
    "Coverage_Ratio",
    "Coverage_Status",
    "Status",
    "Message",
]


@dataclass(frozen=True)
class AvailabilityResult:
    sample_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    expected_start: str
    expected_end: str
    output_path: str
    exists: bool
    rows: int
    valid_columns: bool
    first_date: str
    last_date: str
    expected_duration_days: int | str
    actual_coverage_days: int | str
    start_gap_days: int | str
    end_gap_days: int | str
    coverage_ratio: float | str
    coverage_status: str
    status: str
    message: str


@dataclass(frozen=True)
class CoverageTolerances:
    min_coverage_ratio: float = 0.90
    max_start_gap_days: int = 7
    max_end_gap_days: int = 7


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check expanded historical sample data availability")
    parser.add_argument("--samples-config", required=True, type=Path)
    parser.add_argument("--validation-config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--min-coverage-ratio", type=float, default=0.90)
    parser.add_argument("--max-start-gap-days", type=int, default=7)
    parser.add_argument("--max-end-gap-days", type=int, default=7)
    return parser.parse_args()


def load_validation_scenario_ids(path: Path | str) -> set[str]:
    config_path = Path(path)
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to load validation configs.") from exc
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("scenarios"), list):
        raise ValueError("Validation config must define a scenarios list.")
    return {str(item["scenario_id"]) for item in raw["scenarios"] if isinstance(item, dict) and "scenario_id" in item}


def check_samples(
    samples_config: dict[str, Any],
    validation_scenario_ids: set[str],
    tolerances: CoverageTolerances | None = None,
) -> list[AvailabilityResult]:
    selected_tolerances = tolerances or CoverageTolerances()
    return [_check_sample(sample, validation_scenario_ids, selected_tolerances) for sample in samples_config["samples"]]


def write_availability_csv(path: Path | str, results: list[AvailabilityResult]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "Sample_ID": result.sample_id,
            "Scenario_ID": result.scenario_id,
            "Symbol": result.symbol,
            "Timeframe": result.timeframe,
            "Expected_Start": result.expected_start,
            "Expected_End": result.expected_end,
            "Output_Path": result.output_path,
            "Exists": result.exists,
            "Rows": result.rows,
            "Valid_Columns": result.valid_columns,
            "First_Date": result.first_date,
            "Last_Date": result.last_date,
            "Expected_Duration_Days": result.expected_duration_days,
            "Actual_Coverage_Days": result.actual_coverage_days,
            "Start_Gap_Days": result.start_gap_days,
            "End_Gap_Days": result.end_gap_days,
            "Coverage_Ratio": result.coverage_ratio,
            "Coverage_Status": result.coverage_status,
            "Status": result.status,
            "Message": result.message,
        }
        for result in results
    ]
    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(output_path, index=False)
    return output_path


def write_availability_report(
    path: Path | str,
    samples_config: dict[str, Any],
    validation_scenario_ids: set[str],
    results: list[AvailabilityResult],
) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(samples_config, validation_scenario_ids, results), encoding="utf-8")
    return report_path


def main() -> int:
    args = parse_args()
    samples_config = load_sample_config(args.samples_config)
    validation_scenario_ids = load_validation_scenario_ids(args.validation_config)
    tolerances = CoverageTolerances(
        min_coverage_ratio=args.min_coverage_ratio,
        max_start_gap_days=args.max_start_gap_days,
        max_end_gap_days=args.max_end_gap_days,
    )
    results = check_samples(samples_config, validation_scenario_ids, tolerances)
    write_availability_csv(args.output, results)
    write_availability_report(args.report, samples_config, validation_scenario_ids, results)
    print(f"Sample set: {samples_config['sample_set_name']}")
    print(f"Total samples: {len(results)}")
    print(f"Available full: {sum(1 for result in results if result.status == 'AVAILABLE_FULL')}")
    print(f"Available partial: {sum(1 for result in results if result.status == 'AVAILABLE_PARTIAL')}")
    print(f"Missing: {sum(1 for result in results if result.status == 'MISSING')}")
    print(f"Invalid: {sum(1 for result in results if result.status in {'INVALID_COLUMNS', 'EMPTY_FILE', 'READ_ERROR'})}")
    print(f"Output: {args.output}")
    print(f"Report: {args.report}")
    return 0


def _check_sample(
    sample: dict[str, Any],
    validation_scenario_ids: set[str],
    tolerances: CoverageTolerances,
) -> AvailabilityResult:
    sample_id = str(sample["sample_id"])
    output_path = Path(str(sample["output_path"]))
    base = {
        "sample_id": sample_id,
        "scenario_id": sample_id if sample_id in validation_scenario_ids else "",
        "symbol": str(sample["symbol"]),
        "timeframe": str(sample["timeframe"]),
        "expected_start": str(sample["start"]),
        "expected_end": str(sample["end"]),
        "output_path": str(output_path),
    }
    not_applicable = _not_applicable_coverage()
    if not output_path.exists():
        return AvailabilityResult(**base, **not_applicable, exists=False, rows=0, valid_columns=False, first_date="", last_date="", status="MISSING", message="File not found")
    try:
        frame = pd.read_csv(output_path)
    except pd.errors.EmptyDataError:
        return AvailabilityResult(**base, **not_applicable, exists=True, rows=0, valid_columns=False, first_date="", last_date="", status="EMPTY_FILE", message="CSV file is empty")
    except Exception as exc:
        return AvailabilityResult(**base, **not_applicable, exists=True, rows=0, valid_columns=False, first_date="", last_date="", status="READ_ERROR", message=str(exc))
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in frame.columns]
    if missing_columns:
        return AvailabilityResult(
            **base,
            **not_applicable,
            exists=True,
            rows=len(frame),
            valid_columns=False,
            first_date="",
            last_date="",
            status="INVALID_COLUMNS",
            message=f"Missing columns: {', '.join(missing_columns)}",
        )
    if frame.empty:
        return AvailabilityResult(**base, **not_applicable, exists=True, rows=0, valid_columns=True, first_date="", last_date="", status="EMPTY_FILE", message="CSV file has headers but no rows")
    dates = pd.to_datetime(frame["Date"], errors="coerce")
    parseable_dates = dates.dropna()
    if parseable_dates.empty:
        return AvailabilityResult(**base, **not_applicable, exists=True, rows=len(frame), valid_columns=True, first_date="", last_date="", status="EMPTY_FILE", message="CSV file has no parseable Date values")
    coverage = _coverage_metrics(sample, parseable_dates.min(), parseable_dates.max(), tolerances)
    status = "AVAILABLE_FULL" if coverage["coverage_status"] == "FULL" else "AVAILABLE_PARTIAL"
    return AvailabilityResult(
        **base,
        exists=True,
        rows=len(frame),
        valid_columns=True,
        first_date=str(parseable_dates.min()),
        last_date=str(parseable_dates.max()),
        status=status,
        message=_coverage_message(status, coverage),
        **coverage,
    )


def _not_applicable_coverage() -> dict[str, int | float | str]:
    return {
        "expected_duration_days": "",
        "actual_coverage_days": "",
        "start_gap_days": "",
        "end_gap_days": "",
        "coverage_ratio": "",
        "coverage_status": "NOT_APPLICABLE",
    }


def _coverage_metrics(
    sample: dict[str, Any],
    first_date: pd.Timestamp,
    last_date: pd.Timestamp,
    tolerances: CoverageTolerances,
) -> dict[str, int | float | str]:
    expected_start = _as_date(sample["start"])
    expected_end = _as_date(sample["end"])
    first_day = first_date.date()
    last_day = last_date.date()
    expected_duration_days = max((expected_end - expected_start).days, 1)
    actual_coverage_days = max((last_date - first_date).days, 0)
    start_gap_days = max((first_day - expected_start).days, 0)
    end_gap_days = max((expected_end - last_day).days, 0)
    coverage_ratio = min(max(actual_coverage_days / expected_duration_days, 0), 1)
    coverage_status = (
        "FULL"
        if coverage_ratio >= tolerances.min_coverage_ratio
        and start_gap_days <= tolerances.max_start_gap_days
        and end_gap_days <= tolerances.max_end_gap_days
        else "PARTIAL"
    )
    return {
        "expected_duration_days": expected_duration_days,
        "actual_coverage_days": actual_coverage_days,
        "start_gap_days": start_gap_days,
        "end_gap_days": end_gap_days,
        "coverage_ratio": round(coverage_ratio, 6),
        "coverage_status": coverage_status,
    }


def _coverage_message(status: str, coverage: dict[str, int | float | str]) -> str:
    if status == "AVAILABLE_FULL":
        return "File is available with sufficient historical coverage"
    return (
        "File is available but historical coverage is incomplete: "
        f"coverage_ratio={coverage['coverage_ratio']}, "
        f"start_gap_days={coverage['start_gap_days']}, "
        f"end_gap_days={coverage['end_gap_days']}"
    )


def _as_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return pd.to_datetime(str(value)).date()


def _build_report(
    samples_config: dict[str, Any],
    validation_scenario_ids: set[str],
    results: list[AvailabilityResult],
) -> str:
    invalid_statuses = {"INVALID_COLUMNS", "EMPTY_FILE"}
    missing = [result for result in results if result.status == "MISSING"]
    partial = [result for result in results if result.status == "AVAILABLE_PARTIAL"]
    invalid = [result for result in results if result.status in invalid_statuses]
    read_errors = [result for result in results if result.status == "READ_ERROR"]
    lines = [
        "SQRE Expanded Historical Data Availability Report",
        "================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        f"Sample Set: {samples_config['sample_set_name']}",
        f"Total Samples: {len(results)}",
        f"Available Full: {sum(1 for result in results if result.status == 'AVAILABLE_FULL')}",
        f"Available Partial: {len(partial)}",
        f"Missing: {len(missing)}",
        f"Invalid: {len(invalid)}",
        f"Read Errors: {len(read_errors)}",
        "",
        "By Timeframe:",
    ]
    lines.extend(_timeframe_lines(results))
    lines.extend(["", "Partial Samples:"])
    lines.extend(_partial_sample_lines(partial))
    lines.extend(["", "Missing Samples:"])
    lines.extend(_sample_lines(missing, empty_line="- None"))
    lines.extend(["", "Invalid Samples:"])
    lines.extend(_invalid_sample_lines([*invalid, *read_errors]))
    lines.extend(["", "Validation Config Coverage:"])
    lines.extend(_coverage_lines(results, validation_scenario_ids))
    lines.extend(
        [
            "",
            "Notes:",
            "- Missing files are expected until historical samples are downloaded.",
            "- Partial files should not be interpreted as full historical samples.",
            "- This report is diagnostic and research-only.",
            "",
        ]
    )
    return "\n".join(lines)


def _timeframe_lines(results: list[AvailabilityResult]) -> list[str]:
    timeframes = sorted({result.timeframe for result in results})
    return [
        "- "
        f"{timeframe}: total={sum(1 for result in results if result.timeframe == timeframe)}, "
        f"available_full={sum(1 for result in results if result.timeframe == timeframe and result.status == 'AVAILABLE_FULL')}, "
        f"available_partial={sum(1 for result in results if result.timeframe == timeframe and result.status == 'AVAILABLE_PARTIAL')}, "
        f"missing={sum(1 for result in results if result.timeframe == timeframe and result.status == 'MISSING')}, "
        f"invalid={sum(1 for result in results if result.timeframe == timeframe and result.status in {'INVALID_COLUMNS', 'EMPTY_FILE', 'READ_ERROR'})}"
        for timeframe in timeframes
    ]


def _sample_lines(results: list[AvailabilityResult], *, empty_line: str) -> list[str]:
    if not results:
        return [empty_line]
    return [f"- {result.sample_id}: {result.output_path}" for result in results]


def _partial_sample_lines(results: list[AvailabilityResult]) -> list[str]:
    if not results:
        return ["- None"]
    return [
        "- "
        f"{result.sample_id}: {result.output_path}, "
        f"expected={result.expected_start} -> {result.expected_end}, "
        f"actual={result.first_date} -> {result.last_date}, "
        f"coverage_ratio={result.coverage_ratio}, "
        f"start_gap_days={result.start_gap_days}, "
        f"end_gap_days={result.end_gap_days}"
        for result in results
    ]


def _invalid_sample_lines(results: list[AvailabilityResult]) -> list[str]:
    if not results:
        return ["- None"]
    return [f"- {result.sample_id}: status={result.status}, message={result.message}" for result in results]


def _coverage_lines(results: list[AvailabilityResult], validation_scenario_ids: set[str]) -> list[str]:
    covered = [result for result in results if result.sample_id in validation_scenario_ids]
    missing = [result for result in results if result.sample_id not in validation_scenario_ids]
    lines = [
        f"- Samples covered by validation config: {len(covered)} / {len(results)}",
        f"- Samples missing validation scenario: {len(missing)}",
    ]
    lines.extend(_sample_lines(missing, empty_line="- All samples are covered by validation scenarios."))
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
