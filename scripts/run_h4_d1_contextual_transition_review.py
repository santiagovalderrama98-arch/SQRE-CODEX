#!/usr/bin/env python3
"""Run SQRE H4/D1 contextual transition review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_d1_contextual_transition_review import (  # noqa: E402
    H4D1ContextualTransitionReviewConfig,
    run_h4_d1_contextual_transition_review,
)


def parse_args() -> argparse.Namespace:
    defaults = H4D1ContextualTransitionReviewConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4/D1 contextual transition review")
    parser.add_argument("--h4-combined-context-dir", type=Path, default=defaults.h4_combined_context_dir)
    parser.add_argument("--d1-regime-normalized-dir", type=Path, default=defaults.d1_regime_normalized_dir)
    parser.add_argument("--d1-regime-outcome-review-dir", type=Path, default=defaults.d1_regime_outcome_review_dir)
    parser.add_argument("--d1-state-deep-dive-dir", type=Path, default=defaults.d1_state_deep_dive_dir)
    parser.add_argument("--h4-d1-structural-research-dir", type=Path, default=defaults.h4_d1_structural_research_dir)
    parser.add_argument("--h4-d1-validation-dir", type=Path, default=defaults.h4_d1_validation_dir)
    parser.add_argument("--partial-complement-dir", type=Path, default=defaults.partial_complement_dir)
    parser.add_argument("--partial-validation-dir", type=Path, default=defaults.partial_validation_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--h4-timeframe", default=defaults.h4_timeframe)
    parser.add_argument("--d1-timeframe", default=defaults.d1_timeframe)
    parser.add_argument("--baseline-h4-scenario-count", type=int, default=defaults.baseline_h4_scenario_count)
    parser.add_argument("--baseline-d1-scenario-count", type=int, default=defaults.baseline_d1_scenario_count)
    parser.add_argument("--minimum-context-count", type=int, default=defaults.minimum_context_count)
    parser.add_argument("--minimum-d1-regime-count", type=int, default=defaults.minimum_d1_regime_count)
    parser.add_argument("--allow-partial-context", action=argparse.BooleanOptionalAction, default=defaults.allow_partial_context)
    parser.add_argument("--partial-sample-label", default=defaults.partial_sample_label)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4D1ContextualTransitionReviewConfig(
        h4_combined_context_dir=args.h4_combined_context_dir,
        d1_regime_normalized_dir=args.d1_regime_normalized_dir,
        d1_regime_outcome_review_dir=args.d1_regime_outcome_review_dir,
        d1_state_deep_dive_dir=args.d1_state_deep_dive_dir,
        h4_d1_structural_research_dir=args.h4_d1_structural_research_dir,
        h4_d1_validation_dir=args.h4_d1_validation_dir,
        partial_complement_dir=args.partial_complement_dir,
        partial_validation_dir=args.partial_validation_dir,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        h4_timeframe=args.h4_timeframe,
        d1_timeframe=args.d1_timeframe,
        baseline_h4_scenario_count=args.baseline_h4_scenario_count,
        baseline_d1_scenario_count=args.baseline_d1_scenario_count,
        minimum_context_count=args.minimum_context_count,
        minimum_d1_regime_count=args.minimum_d1_regime_count,
        allow_partial_context=args.allow_partial_context,
        partial_sample_label=args.partial_sample_label,
    )
    print(f"H4 combined context directory: {config.h4_combined_context_dir}")
    print(f"D1 regime normalized directory: {config.d1_regime_normalized_dir}")
    print(f"D1 regime outcome review directory: {config.d1_regime_outcome_review_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_d1_contextual_transition_review(config)
    except Exception as exc:
        print(f"H4/D1 contextual transition review failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4/D1 contextual transition review completed")
    print(f"Source rows: {len(result.source_inventory)}")
    print(f"Scenario context map rows: {len(result.scenario_context_map)}")
    print(f"Context rows: {len(result.context_inventory)}")
    if summary:
        print(f"Mapped context count: {summary.mapped_context_count}")
        print(f"Unmapped context count: {summary.unmapped_context_count}")
        print(f"Readiness flag: {summary.h4_d1_contextual_readiness_flag}")
        print(f"Dominant interpretation: {summary.dominant_h4_d1_contextual_interpretation}")
    print(f"Summary path: {result.output_dir / 'h4_d1_contextual_transition_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
