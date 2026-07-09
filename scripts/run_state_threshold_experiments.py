#!/usr/bin/env python3
"""Run SQRE Phase 7.4.2 state threshold experiments."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.state_threshold_experiments import build_experiment_runs, load_state_threshold_experiment_config
from sqre.state_threshold_experiments.state_threshold_experiment_pipeline import run_state_threshold_experiments


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE state threshold experiments")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary-csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--profile")
    parser.add_argument("--scenario")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    print("SQRE state threshold experiments started")
    try:
        config = load_state_threshold_experiment_config(args.config)
        all_runs = build_experiment_runs(config, args.output_dir)
        selected_runs = build_experiment_runs(
            config,
            args.output_dir,
            profile_filter=args.profile,
            scenario_filter=args.scenario,
        )
        print(f"Experiment name: {config.experiment_name}")
        print(f"Base scenarios: {len(config.base_scenarios)}")
        print(f"Runs configured: {len(all_runs)}")
        print(f"Runs selected: {len(selected_runs)}")
        summary = run_state_threshold_experiments(
            config_path=args.config,
            output_dir=args.output_dir,
            summary_csv_path=args.summary_csv,
            report_path=args.report,
            profile_filter=args.profile,
            scenario_filter=args.scenario,
            strict=args.strict,
            skip_existing=args.skip_existing,
        )
    except Exception as exc:
        logging.exception("State threshold experiments failed")
        print(f"State threshold experiments failed: {exc}")
        return 1

    _print_run_statuses(args.summary_csv)
    print("State threshold experiment summary written:")
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
