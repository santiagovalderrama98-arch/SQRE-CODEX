#!/usr/bin/env python3
"""Run SQRE Research Reference Store Usage Review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.research_reference_store_usage_review import (  # noqa: E402
    ResearchReferenceStoreUsageReviewConfig,
    ResearchReferenceStoreUsageReviewPipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE research reference store usage review")
    parser.add_argument("--reference-store-dir", type=Path, default=Path("data/research/research_reference_store_design"))
    parser.add_argument(
        "--interpretation-dir", type=Path, default=Path("data/research/h4_d1_forward_outcome_interpretation_review")
    )
    parser.add_argument("--same-time-alignment-dir", type=Path, default=Path("data/research/h4_d1_same_time_alignment_table"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/research/research_reference_store_usage_review"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/research/research_reference_store_usage_review/research_reference_store_usage_review_report.txt"),
    )
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--h4-timeframe", default="H4")
    parser.add_argument("--d1-timeframe", default="D1")
    parser.add_argument("--preferred-horizons", default="1,2,3,6,12")
    parser.add_argument("--minimum-reference-sample-size", type=int, default=10)
    parser.add_argument("--minimum-core-reference-sample-size", type=int, default=20)
    parser.add_argument("--maximum-reference-dispersion-pips", type=float, default=80.0)
    parser.add_argument("--maximum-scenarios", type=int, default=500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ResearchReferenceStoreUsageReviewConfig(
        reference_store_dir=args.reference_store_dir,
        interpretation_dir=args.interpretation_dir,
        same_time_alignment_dir=args.same_time_alignment_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        preferred_horizons=_parse_horizons(args.preferred_horizons),
        minimum_reference_sample_size=args.minimum_reference_sample_size,
        minimum_core_reference_sample_size=args.minimum_core_reference_sample_size,
        maximum_reference_dispersion_pips=args.maximum_reference_dispersion_pips,
        maximum_scenarios=args.maximum_scenarios,
    )
    print(f"Reference store dir: {config.reference_store_dir}")
    print(f"Interpretation dir: {config.interpretation_dir}")
    print(f"Same-time alignment dir: {config.same_time_alignment_dir}")
    print(f"Output dir: {config.output_dir}")
    result = ResearchReferenceStoreUsageReviewPipeline(config).run()
    summary = result.summary
    print("Research reference store usage review completed")
    if summary:
        print(f"Research references: {summary.research_reference_count}")
        print(f"Usage scenarios: {summary.usage_scenario_count}")
        print(f"Matched scenarios: {summary.matched_scenario_count}")
        print(f"Unmatched scenarios: {summary.unmatched_scenario_count}")
        print(f"Readiness flag: {summary.research_reference_store_usage_readiness_flag}")
    print(f"Report: {result.report_path}")
    return 0


def _parse_horizons(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main())
