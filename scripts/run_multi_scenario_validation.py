#!/usr/bin/env python3
"""Run SQRE multi-scenario validation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.validation.models import FAILED, MISSING_INPUT
from sqre.validation.runner import run_multi_scenario_validation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE multi-scenario validation")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/validation"))
    parser.add_argument("--report", type=Path, default=Path("data/validation/multi_scenario_validation_report.txt"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/validation/multi_scenario_validation_summary.csv"))
    parser.add_argument("--scenario", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)

    print("SQRE multi-scenario validation started")
    try:
        summary, results, _metrics = run_multi_scenario_validation(
            config_path=args.config,
            output_dir=args.output_dir,
            report_path=args.report,
            summary_csv_path=args.summary_csv,
            scenario_id=args.scenario,
            strict=args.strict,
            skip_existing=args.skip_existing,
        )
    except Exception as exc:
        logging.exception("Multi-scenario validation failed")
        print(f"Multi-scenario validation failed: {exc}")
        return 1

    print(f"Validation name: {summary.validation_name}")
    print(f"Scenarios configured: {summary.scenarios_configured}")
    print(f"Scenarios selected: {summary.scenarios_selected}")
    print("")
    for result in results:
        print(f"Scenario: {result.scenario_id}")
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        print("")
    print("Validation summary written:")
    print(f"- {summary.summary_csv_path}")
    print(f"- {summary.report_path}")

    if args.strict and any(result.status in {FAILED, MISSING_INPUT} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
