#!/usr/bin/env python3
"""Run SQRE H4 timestamped state/transition output generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_timestamped_state_transition_outputs import (  # noqa: E402
    H4TimestampedStateTransitionConfig,
    run_h4_timestamped_state_transition_outputs,
)


def parse_args() -> argparse.Namespace:
    defaults = H4TimestampedStateTransitionConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4 timestamped state/transition output generation")
    parser.add_argument("--h4-d1-validation-dir", type=Path, default=defaults.h4_d1_validation_dir)
    parser.add_argument("--h4-d1-structural-research-dir", type=Path, default=defaults.h4_d1_structural_research_dir)
    parser.add_argument("--validation-config", type=Path, default=defaults.validation_config)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--symbol", default=defaults.symbol)
    parser.add_argument("--timeframe", default=defaults.timeframe)
    parser.add_argument("--minimum-scenario-coverage-ratio", type=float, default=defaults.minimum_scenario_coverage_ratio)
    parser.add_argument("--allow-regeneration", default=str(defaults.allow_regeneration).lower())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4TimestampedStateTransitionConfig(
        h4_d1_validation_dir=args.h4_d1_validation_dir,
        h4_d1_structural_research_dir=args.h4_d1_structural_research_dir,
        validation_config=args.validation_config,
        output_dir=args.output_dir,
        report_path=args.report,
        symbol=args.symbol,
        timeframe=args.timeframe,
        minimum_scenario_coverage_ratio=args.minimum_scenario_coverage_ratio,
        allow_regeneration=_parse_bool(args.allow_regeneration),
    )
    print(f"H4/D1 validation directory: {config.h4_d1_validation_dir}")
    print(f"H4/D1 structural research directory: {config.h4_d1_structural_research_dir}")
    print(f"Validation config: {config.validation_config}")
    print(f"Output directory: {config.output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_timestamped_state_transition_outputs(config)
    except Exception as exc:
        print(f"H4 timestamped state/transition output generation failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4 timestamped state/transition output generation completed")
    print(f"Source inventory rows: {len(result.source_inventory)}")
    print(f"Scenario inventory rows: {len(result.scenario_inventory)}")
    print(f"Timestamped market state rows: {len(result.market_state_rows)}")
    print(f"Timestamped state transition rows: {len(result.transition_rows)}")
    print(f"Coverage review rows: {len(result.coverage_review)}")
    print(f"Missing output review rows: {len(result.missing_output_review)}")
    if summary:
        print(f"Dominant output coverage class: {summary.dominant_output_coverage_class}")
        print(
            "H4 timestamped state transition readiness flag: "
            f"{summary.h4_timestamped_state_transition_readiness_flag}"
        )
        print(f"Recommended follow-up: {summary.recommended_follow_up}")
    print(f"Summary path: {result.output_dir / 'h4_timestamped_state_transition_generation_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


if __name__ == "__main__":
    sys.exit(main())
