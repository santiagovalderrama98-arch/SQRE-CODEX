#!/usr/bin/env python3
"""Run Research Reference Store Design."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.research_reference_store_design import (  # noqa: E402
    ResearchReferenceStoreDesignConfig,
    ResearchReferenceStoreDesignPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE Research Reference Store Design")
    parser.add_argument("--interpretation-dir", type=Path, required=True)
    parser.add_argument("--forward-outcome-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--minimum-core-reference-sample-size", type=int, default=20)
    parser.add_argument("--minimum-supporting-reference-sample-size", type=int, default=10)
    parser.add_argument("--maximum-core-dispersion-pips", type=float, default=40.0)
    parser.add_argument("--maximum-supporting-dispersion-pips", type=float, default=80.0)
    parser.add_argument("--require-stable-horizon-context", type=_bool, default=False)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ResearchReferenceStoreDesignConfig(
        interpretation_dir=args.interpretation_dir,
        forward_outcome_dir=args.forward_outcome_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_core_reference_sample_size=args.minimum_core_reference_sample_size,
        minimum_supporting_reference_sample_size=args.minimum_supporting_reference_sample_size,
        maximum_core_dispersion_pips=args.maximum_core_dispersion_pips,
        maximum_supporting_dispersion_pips=args.maximum_supporting_dispersion_pips,
        require_stable_horizon_context=args.require_stable_horizon_context,
    )
    print(f"Interpretation directory: {config.interpretation_dir}")
    print(f"Forward outcome directory: {config.forward_outcome_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    result = ResearchReferenceStoreDesignPipeline(config).run()
    summary = result.summary
    print("Research reference store design completed")
    if summary:
        print(f"Outcome profile count: {summary.outcome_profile_count}")
        print(f"Reference candidate count: {summary.reference_candidate_count}")
        print(f"Included reference count: {summary.included_reference_count}")
        print(f"Core reference count: {summary.core_reference_count}")
        print(f"Supporting reference count: {summary.supporting_reference_count}")
        print(f"Watchlist reference count: {summary.watchlist_reference_count}")
        print(f"Excluded reference count: {summary.excluded_reference_count}")
        print(f"Primary reference granularity: {summary.primary_reference_granularity}")
        print(f"Primary reference horizon: {summary.primary_reference_horizon}")
        print(f"Readiness class: {summary.research_reference_store_readiness_class}")
        print(f"Readiness flag: {summary.research_reference_store_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {config.output_dir / 'research_reference_store_design_summary.csv'}")
    print(f"Report path: {config.report_path}")
    return 0


def _bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("Expected true or false.")


if __name__ == "__main__":
    raise SystemExit(main())
