#!/usr/bin/env python3
"""Run SQRE H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_temporal_alignment_feasibility_review import (  # noqa: E402
    H4D1TemporalAlignmentFeasibilityConfig,
    run_h4_d1_temporal_alignment_feasibility_review,
)


def parse_args() -> argparse.Namespace:
    defaults = H4D1TemporalAlignmentFeasibilityConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 temporal alignment feasibility review")
    parser.add_argument("--h4-combined-context-dir", type=Path, default=defaults.h4_combined_context_dir)
    parser.add_argument("--h4-d1-structural-research-dir", type=Path, default=defaults.h4_d1_structural_research_dir)
    parser.add_argument("--h4-d1-validation-dir", type=Path, default=defaults.h4_d1_validation_dir)
    parser.add_argument("--d1-regime-normalized-dir", type=Path, default=defaults.d1_regime_normalized_dir)
    parser.add_argument("--d1-regime-outcome-review-dir", type=Path, default=defaults.d1_regime_outcome_review_dir)
    parser.add_argument("--d1-state-deep-dive-dir", type=Path, default=defaults.d1_state_deep_dive_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--h4-timeframe", default=defaults.h4_timeframe)
    parser.add_argument("--d1-timeframe", default=defaults.d1_timeframe)
    parser.add_argument(
        "--minimum-temporal-key-coverage-ratio",
        type=float,
        default=defaults.minimum_temporal_key_coverage_ratio,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1TemporalAlignmentFeasibilityConfig(
        h4_combined_context_dir=args.h4_combined_context_dir,
        h4_d1_structural_research_dir=args.h4_d1_structural_research_dir,
        h4_d1_validation_dir=args.h4_d1_validation_dir,
        d1_regime_normalized_dir=args.d1_regime_normalized_dir,
        d1_regime_outcome_review_dir=args.d1_regime_outcome_review_dir,
        d1_state_deep_dive_dir=args.d1_state_deep_dive_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        minimum_temporal_key_coverage_ratio=args.minimum_temporal_key_coverage_ratio,
    )
    print(f"H4 combined context directory: {config.h4_combined_context_dir}")
    print(f"H4/D1 structural research directory: {config.h4_d1_structural_research_dir}")
    print(f"D1 regime outcome review directory: {config.d1_regime_outcome_review_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_d1_temporal_alignment_feasibility_review(config)
    except Exception as exc:
        print(f"H4/D1 temporal alignment feasibility review failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4/D1 temporal alignment feasibility review completed")
    print(f"Source rows: {len(result.source_inventory)}")
    print(f"Temporal key inventory rows: {len(result.temporal_key_inventory)}")
    print(f"Alignment candidate rows: {len(result.alignment_candidates)}")
    print(f"Missing key review rows: {len(result.missing_keys)}")
    if summary:
        print(f"Dominant alignment feasibility class: {summary.dominant_alignment_feasibility_class}")
        print(f"Temporal alignment readiness flag: {summary.temporal_alignment_readiness_flag}")
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {result.output_dir / 'h4_d1_temporal_alignment_feasibility_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
