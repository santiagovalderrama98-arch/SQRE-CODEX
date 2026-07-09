#!/usr/bin/env python3
"""Run SQRE Phase 7.4.1 calibration experiments."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.calibration_experiments import build_experiment_runs, load_calibration_experiment_config
from sqre.calibration_experiments.calibration_experiment_pipeline import run_calibration_experiments


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE calibration experiments")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary-csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--experiment")
    parser.add_argument("--experiment-type", choices=["DURATION", "SAMPLE_SIZE"])
    parser.add_argument("--scenario")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    print("SQRE calibration experiments started")
    try:
        config = load_calibration_experiment_config(args.config)
        all_runs = build_experiment_runs(config, args.output_dir)
        selected_runs = build_experiment_runs(
            config,
            args.output_dir,
            experiment_filter=args.experiment,
            experiment_type_filter=args.experiment_type,
            scenario_filter=args.scenario,
        )
        print(f"Experiment name: {config.experiment_name}")
        print(f"Base scenarios: {len(config.base_scenarios)}")
        print(f"Experiment runs configured: {len(all_runs)}")
        print(f"Experiment runs selected: {len(selected_runs)}")
        summary = run_calibration_experiments(
            config_path=args.config,
            output_dir=args.output_dir,
            summary_csv_path=args.summary_csv,
            report_path=args.report,
            experiment_filter=args.experiment,
            experiment_type_filter=args.experiment_type,
            scenario_filter=args.scenario,
            strict=args.strict,
            skip_existing=args.skip_existing,
        )
    except Exception as exc:
        logging.exception("Calibration experiments failed")
        print(f"Calibration experiments failed: {exc}")
        return 1

    _print_run_statuses(args.summary_csv)
    print("Calibration experiment summary written:")
    print(f"- {summary.output_path}")
    print(f"- {summary.report_path}")
    return 0


def _print_run_statuses(summary_csv: Path) -> None:
    try:
        import pandas as pd
    except ImportError:
        return
    if not summary_csv.exists():
        return
    frame = pd.read_csv(summary_csv)
    for _, row in frame.iterrows():
        print(f"Run: {row['Experiment_Run_ID']}")
        print(f"Status: {row['Status']}")
        print(f"Message: {row['Message']}")


if __name__ == "__main__":
    raise SystemExit(main())
