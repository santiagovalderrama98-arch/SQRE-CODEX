#!/usr/bin/env python3
"""Build SQRE Phase 7.4.5 master historical calibration summary."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.master_calibration_summary import MasterCalibrationSummaryConfig, build_master_calibration_summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SQRE master historical calibration summary")
    parser.add_argument("--summary-csv", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--dedupe-key", default="Scenario_ID")
    parser.add_argument("--dedupe-policy", choices=["first", "last", "error"], default="last")
    parser.add_argument("--allow-missing-inputs", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    config = MasterCalibrationSummaryConfig(
        dedupe_key=args.dedupe_key,
        dedupe_policy=args.dedupe_policy,
        allow_missing_inputs=args.allow_missing_inputs,
    )
    print("SQRE master historical calibration summary started")
    print(f"Input summaries requested: {len(args.summary_csv)}")

    try:
        result = build_master_calibration_summary(
            summary_csv_paths=args.summary_csv,
            output_path=args.output,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("Master historical calibration summary failed")
        print(f"Master historical calibration summary failed: {exc}")
        return 1

    print(f"Input summaries found: {len(result.found_files)}")
    print(f"Input summaries missing: {len(result.missing_files)}")
    print(f"Rows loaded: {result.rows_loaded}")
    print(f"Rows retained: {result.rows_retained}")
    print(f"Duplicate Scenario_IDs: {len(result.duplicate_scenario_ids)}")
    print(f"Timeframes covered: {', '.join(sorted(result.timeframe_counts)) if result.timeframe_counts else 'NONE'}")
    print("Master historical calibration summary written:")
    print(f"- {result.output_path}")
    print(f"- {result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
