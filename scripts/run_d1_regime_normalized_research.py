#!/usr/bin/env python3
"""Run D1 regime-normalized price outcome research."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.d1_regime_normalized_research.config import load_d1_regime_research_config
from sqre.d1_regime_normalized_research.d1_regime_normalized_research_pipeline import (
    run_d1_regime_normalized_research,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run D1 regime-normalized price outcome research")
    parser.add_argument("--config", default="configs/validation/d1_regime_normalized_research.yaml")
    parser.add_argument(
        "--validation-summary",
        default="data/validation/h4_d1_structural_research/h4_d1_validation_summary.csv",
    )
    parser.add_argument("--validation-output-dir", default="data/validation/h4_d1_structural_research")
    parser.add_argument("--output-dir", default="data/research/d1_regime_normalized_research")
    parser.add_argument(
        "--report",
        default="data/research/d1_regime_normalized_research/d1_regime_normalized_research_report.txt",
    )
    parser.add_argument("--minimum-sample-size", type=int, default=None)
    parser.add_argument("--high-regime-sensitivity-threshold", type=float, default=None)
    parser.add_argument("--moderate-regime-sensitivity-threshold", type=float, default=None)
    parser.add_argument("--forward-range-stability-threshold", type=float, default=None)
    parser.add_argument("--minimum-regime-count", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    try:
        config = _apply_overrides(args)
        print("SQRE D1 regime-normalized research started")
        print(f"Config: {args.config}")
        print(f"Validation summary: {args.validation_summary}")
        print(f"Validation output directory: {args.validation_output_dir}")
        print(f"Output directory: {args.output_dir}")
        print(f"Report: {args.report}")
        result = run_d1_regime_normalized_research(
            config_path=args.config,
            validation_summary_path=args.validation_summary,
            validation_output_dir=args.validation_output_dir,
            output_dir=args.output_dir,
            report_path=args.report,
            overrides=config,
        )
    except Exception as exc:
        print(f"D1 regime-normalized research failed: {exc}")
        return 1

    print("D1 regime-normalized research completed")
    print(f"D1 scenarios loaded: {result.scenarios_loaded}")
    print(f"D1 regimes loaded: {result.regimes_loaded}")
    print(f"Condition profiles generated: {len(result.condition_profiles)}")
    print(f"State outcome profiles generated: {len(result.state_profiles)}")
    print(f"Transition outcome profiles generated: {len(result.transition_profiles)}")
    print(f"Scenario inventory path: {Path(args.output_dir) / 'd1_regime_scenario_inventory.csv'}")
    print(f"Condition outcomes path: {Path(args.output_dir) / 'd1_regime_condition_outcomes.csv'}")
    print(f"Normalized condition profiles path: {Path(args.output_dir) / 'd1_regime_normalized_condition_profiles.csv'}")
    print(f"State outcome profiles path: {Path(args.output_dir) / 'd1_regime_state_outcome_profiles.csv'}")
    print(f"Transition outcome profiles path: {Path(args.output_dir) / 'd1_regime_transition_outcome_profiles.csv'}")
    print(f"Research summary path: {Path(args.output_dir) / 'd1_regime_research_summary.csv'}")
    print(f"Report path: {args.report}")
    return 0


def _apply_overrides(args: argparse.Namespace):
    config = load_d1_regime_research_config(args.config)
    values = config.__dict__.copy()
    for field, arg_name in {
        "minimum_sample_size": "minimum_sample_size",
        "high_regime_sensitivity_threshold": "high_regime_sensitivity_threshold",
        "moderate_regime_sensitivity_threshold": "moderate_regime_sensitivity_threshold",
        "forward_range_stability_threshold": "forward_range_stability_threshold",
        "minimum_regime_count": "minimum_regime_count",
    }.items():
        value = getattr(args, arg_name)
        if value is not None:
            values[field] = value
    return type(config)(**values)


if __name__ == "__main__":
    raise SystemExit(main())
