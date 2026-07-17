#!/usr/bin/env python3
"""Run SQRE H4 transition outcome deep dive."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_transition_outcome_deep_dive.config import H4TransitionOutcomeDeepDiveConfig
from sqre.h4_transition_outcome_deep_dive.h4_transition_outcome_deep_dive_pipeline import run_h4_transition_outcome_deep_dive


def _bool_arg(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE H4 transition outcome deep dive")
    parser.add_argument(
        "--h4-d1-research-dir",
        type=Path,
        default=Path("data/research/h4_d1_structural_research"),
    )
    parser.add_argument(
        "--validation-output-dir",
        type=Path,
        default=Path("data/validation/h4_d1_structural_research"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/research/h4_transition_outcome_deep_dive"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/h4_transition_outcome_deep_dive/h4_transition_outcome_deep_dive_report.txt"),
    )
    parser.add_argument("--minimum-total-sample-size", type=int, default=20)
    parser.add_argument("--minimum-scenario-count", type=int, default=2)
    parser.add_argument("--full-scenario-count", type=int, default=4)
    parser.add_argument("--high-dispersion-threshold", type=float, default=0.35)
    parser.add_argument("--moderate-dispersion-threshold", type=float, default=0.20)
    parser.add_argument("--include-sample-constrained-observations", type=_bool_arg, default=True)
    parser.add_argument(
        "--exclude-sample-constrained-observations",
        action="store_true",
        help="Exclude sample-constrained H4 observations from descriptive outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4TransitionOutcomeDeepDiveConfig(
        minimum_total_sample_size=args.minimum_total_sample_size,
        minimum_scenario_count=args.minimum_scenario_count,
        full_scenario_count=args.full_scenario_count,
        high_dispersion_threshold=args.high_dispersion_threshold,
        moderate_dispersion_threshold=args.moderate_dispersion_threshold,
        include_sample_constrained_observations=(
            args.include_sample_constrained_observations and not args.exclude_sample_constrained_observations
        ),
    )
    print(f"H4/D1 research directory: {args.h4_d1_research_dir}")
    print(f"Validation output directory: {args.validation_output_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_h4_transition_outcome_deep_dive(
            h4_d1_research_dir=args.h4_d1_research_dir,
            validation_output_dir=args.validation_output_dir,
            output_dir=args.output_dir,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        print(f"H4 transition outcome deep dive failed: {exc}", file=sys.stderr)
        return 1
    print("H4 transition outcome deep dive completed")
    print(f"Price profiles loaded: {result.price_profiles_loaded}")
    print(f"Scenario outcomes loaded: {result.scenario_outcomes_loaded}")
    print(f"Selected profiles: {len(result.selected_profiles)}")
    print(f"Scenario breakdown rows: {len(result.scenario_breakdown_rows)}")
    print(f"Outcome statistics rows: {len(result.outcome_statistics_rows)}")
    print(f"Comparison rows: {len(result.comparison_rows)}")
    print(f"Transition family summary rows: {len(result.family_summary_rows)}")
    print(f"Summary rows: {len(result.summary_rows)}")
    print(f"Profile inventory path: {result.output_dir / 'h4_transition_deep_dive_profile_inventory.csv'}")
    print(f"Scenario breakdown path: {result.output_dir / 'h4_transition_scenario_breakdown.csv'}")
    print(f"Outcome statistics path: {result.output_dir / 'h4_transition_outcome_statistics.csv'}")
    print(f"Scenario comparison path: {result.output_dir / 'h4_transition_scenario_comparison_matrix.csv'}")
    print(f"Transition family summary path: {result.output_dir / 'h4_transition_family_summary.csv'}")
    print(f"Summary path: {result.output_dir / 'h4_transition_deep_dive_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
