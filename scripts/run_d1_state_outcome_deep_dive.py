#!/usr/bin/env python3
"""Run D1 research-ready state outcome deep dive."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.d1_state_outcome_deep_dive.config import D1StateOutcomeDeepDiveConfig
from sqre.d1_state_outcome_deep_dive.d1_state_outcome_deep_dive_pipeline import run_d1_state_outcome_deep_dive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE D1 state outcome deep dive")
    parser.add_argument("--outcome-review-dir", default="data/research/d1_regime_outcome_review")
    parser.add_argument("--regime-research-dir", default="data/research/d1_regime_normalized_research")
    parser.add_argument("--output-dir", default="data/research/d1_state_outcome_deep_dive")
    parser.add_argument(
        "--report",
        default="data/research/d1_state_outcome_deep_dive/d1_state_outcome_deep_dive_report.txt",
    )
    parser.add_argument("--minimum-total-sample-size", type=int, default=20)
    parser.add_argument("--minimum-regime-count", type=int, default=2)
    parser.add_argument("--full-regime-count", type=int, default=4)
    parser.add_argument("--high-dispersion-threshold", type=float, default=0.35)
    parser.add_argument("--moderate-dispersion-threshold", type=float, default=0.20)
    parser.add_argument("--include-regime-sensitive-observations", default="true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = D1StateOutcomeDeepDiveConfig(
        minimum_total_sample_size=args.minimum_total_sample_size,
        minimum_regime_count=args.minimum_regime_count,
        full_regime_count=args.full_regime_count,
        high_dispersion_threshold=args.high_dispersion_threshold,
        moderate_dispersion_threshold=args.moderate_dispersion_threshold,
        include_regime_sensitive_observations=_parse_bool(args.include_regime_sensitive_observations),
    )

    print(f"Outcome review directory: {args.outcome_review_dir}")
    print(f"Regime research directory: {args.regime_research_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_d1_state_outcome_deep_dive(
            args.outcome_review_dir,
            args.regime_research_dir,
            args.output_dir,
            args.report,
            config,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"D1 state outcome deep dive failed: {exc}")
        return 1

    ready = sum(1 for profile in result.selected_profiles if profile.profile_type == "RESEARCH_READY")
    sensitive = sum(1 for profile in result.selected_profiles if profile.profile_type == "REGIME_SENSITIVE_OBSERVATION")
    print("D1 state outcome deep dive completed")
    print(f"Research-ready profiles loaded: {result.research_ready_profiles_loaded}")
    print(f"Regime-sensitive profiles loaded: {result.regime_sensitive_profiles_loaded}")
    print(f"Regime outcomes loaded: {result.regime_outcomes_loaded}")
    print(f"Research-ready state profiles selected: {ready}")
    print(f"Regime-sensitive observation profiles selected: {sensitive}")
    print(f"Regime breakdown rows: {len(result.regime_breakdown_rows)}")
    print(f"Outcome statistics rows: {len(result.outcome_statistics_rows)}")
    print(f"Comparison matrix rows: {len(result.comparison_rows)}")
    print(f"Summary rows: {len(result.summary_rows)}")
    print(f"Report path: {args.report}")
    return 0


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


if __name__ == "__main__":
    raise SystemExit(main())
