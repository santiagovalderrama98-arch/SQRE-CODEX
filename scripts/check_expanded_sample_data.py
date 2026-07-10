#!/usr/bin/env python3
"""Check data availability for SQRE expanded historical samples."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
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
    status: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check expanded historical sample data availability")
    parser.add_argument("--samples-config", required=True, type=Path)
    parser.add_argument("--validation-config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
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


def check_samples(samples_config: dict[str, Any], validation_scenario_ids: set[str]) -> list[AvailabilityResult]:
    return [_check_sample(sample, validation_scenario_ids) for sample in samples_config["samples"]]


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
    results = check_samples(samples_config, validation_scenario_ids)
    write_availability_csv(args.output, results)
    write_availability_report(args.report, samples_config, validation_scenario_ids, results)
    print(f"Sample set: {samples_config['sample_set_name']}")
    print(f"Total samples: {len(results)}")
    print(f"Available: {sum(1 for result in results if result.status == 'AVAILABLE')}")
    print(f"Missing: {sum(1 for result in results if result.status == 'MISSING')}")
    print(f"Invalid: {sum(1 for result in results if result.status in {'INVALID_COLUMNS', 'EMPTY_FILE', 'READ_ERROR'})}")
    print(f"Output: {args.output}")
    print(f"Report: {args.report}")
    return 0


def _check_sample(sample: dict[str, Any], validation_scenario_ids: set[str]) -> AvailabilityResult:
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
    if not output_path.exists():
        return AvailabilityResult(**base, exists=False, rows=0, valid_columns=False, first_date="", last_date="", status="MISSING", message="File not found")
    try:
        frame = pd.read_csv(output_path)
    except pd.errors.EmptyDataError:
        return AvailabilityResult(**base, exists=True, rows=0, valid_columns=False, first_date="", last_date="", status="EMPTY_FILE", message="CSV file is empty")
    except Exception as exc:
        return AvailabilityResult(**base, exists=True, rows=0, valid_columns=False, first_date="", last_date="", status="READ_ERROR", message=str(exc))
    missing_columns = [column for column in EXPECTED_COLUMNS if column not in frame.columns]
    if missing_columns:
        return AvailabilityResult(
            **base,
            exists=True,
            rows=len(frame),
            valid_columns=False,
            first_date="",
            last_date="",
            status="INVALID_COLUMNS",
            message=f"Missing columns: {', '.join(missing_columns)}",
        )
    if frame.empty:
        return AvailabilityResult(**base, exists=True, rows=0, valid_columns=True, first_date="", last_date="", status="EMPTY_FILE", message="CSV file has headers but no rows")
    dates = pd.to_datetime(frame["Date"], errors="coerce")
    return AvailabilityResult(
        **base,
        exists=True,
        rows=len(frame),
        valid_columns=True,
        first_date=str(dates.min()),
        last_date=str(dates.max()),
        status="AVAILABLE",
        message="File is available with expected OHLC columns",
    )


def _build_report(
    samples_config: dict[str, Any],
    validation_scenario_ids: set[str],
    results: list[AvailabilityResult],
) -> str:
    invalid_statuses = {"INVALID_COLUMNS", "EMPTY_FILE", "READ_ERROR"}
    missing = [result for result in results if result.status == "MISSING"]
    invalid = [result for result in results if result.status in invalid_statuses]
    lines = [
        "SQRE Expanded Historical Data Availability Report",
        "================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        f"Sample Set: {samples_config['sample_set_name']}",
        f"Total Samples: {len(results)}",
        f"Available: {sum(1 for result in results if result.status == 'AVAILABLE')}",
        f"Missing: {len(missing)}",
        f"Invalid: {len(invalid)}",
        "",
        "By Timeframe:",
    ]
    lines.extend(_timeframe_lines(results))
    lines.extend(["", "Missing Samples:"])
    lines.extend(_sample_lines(missing, empty_line="- None"))
    lines.extend(["", "Validation Config Coverage:"])
    lines.extend(_coverage_lines(results, validation_scenario_ids))
    lines.extend(["", "Notes:", "- Missing files are expected until historical samples are downloaded.", "- This report is diagnostic and research-only.", ""])
    return "\n".join(lines)


def _timeframe_lines(results: list[AvailabilityResult]) -> list[str]:
    timeframes = sorted({result.timeframe for result in results})
    return [
        "- "
        f"{timeframe}: total={sum(1 for result in results if result.timeframe == timeframe)}, "
        f"available={sum(1 for result in results if result.timeframe == timeframe and result.status == 'AVAILABLE')}, "
        f"missing={sum(1 for result in results if result.timeframe == timeframe and result.status == 'MISSING')}"
        for timeframe in timeframes
    ]


def _sample_lines(results: list[AvailabilityResult], *, empty_line: str) -> list[str]:
    if not results:
        return [empty_line]
    return [f"- {result.sample_id}: {result.output_path}" for result in results]


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
