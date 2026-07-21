#!/usr/bin/env python3
"""Run SQRE H4 targeted partial expansion validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_targeted_partial_expansion_validation import (  # noqa: E402
    H4TargetedPartialExpansionValidationConfig,
    run_h4_targeted_partial_expansion_validation,
)


def parse_args() -> argparse.Namespace:
    defaults = H4TargetedPartialExpansionValidationConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4 targeted partial expansion validation")
    parser.add_argument("--feasibility-dir", type=Path, default=defaults.feasibility_dir)
    parser.add_argument("--baseline-validation-dir", type=Path, default=defaults.baseline_validation_dir)
    parser.add_argument("--baseline-research-dir", type=Path, default=defaults.baseline_research_dir)
    parser.add_argument("--output-dir", type=Path, default=defaults.output_dir)
    parser.add_argument("--research-output-dir", type=Path, default=defaults.research_output_dir)
    parser.add_argument("--report", type=Path, default=defaults.report_path)
    parser.add_argument("--candidate-id", default=defaults.candidate_id)
    parser.add_argument("--raw-data-dir", type=Path, default=defaults.raw_data_dir)
    parser.add_argument("--partial-data-dir", type=Path, default=defaults.partial_data_dir)
    parser.add_argument("--pip-size", type=float, default=defaults.pip_size)
    parser.add_argument("--forward-candles", default=",".join(str(value) for value in defaults.forward_candles))
    parser.add_argument("--minimum-sample-size", type=int, default=defaults.minimum_sample_size)
    parser.add_argument(
        "--max-structure-duration-seconds",
        type=int,
        default=defaults.max_structure_duration_seconds,
    )
    parser.add_argument("--partial-sample-label", default=defaults.partial_sample_label)
    parser.add_argument("--allow-partial-validation", default=str(defaults.allow_partial_validation).lower())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4TargetedPartialExpansionValidationConfig(
        feasibility_dir=args.feasibility_dir,
        baseline_validation_dir=args.baseline_validation_dir,
        baseline_research_dir=args.baseline_research_dir,
        output_dir=args.output_dir,
        research_output_dir=args.research_output_dir,
        report_path=args.report,
        candidate_id=args.candidate_id,
        raw_data_dir=args.raw_data_dir,
        partial_data_dir=args.partial_data_dir,
        pip_size=args.pip_size,
        forward_candles=[int(value.strip()) for value in args.forward_candles.split(",") if value.strip()],
        minimum_sample_size=args.minimum_sample_size,
        max_structure_duration_seconds=args.max_structure_duration_seconds,
        partial_sample_label=args.partial_sample_label,
        allow_partial_validation=str(args.allow_partial_validation).strip().lower() in {"true", "1", "yes"},
    )
    print(f"Feasibility directory: {config.feasibility_dir}")
    print(f"Baseline validation directory: {config.baseline_validation_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Research output directory: {config.research_output_dir}")
    print(f"Report: {config.report_path}")
    try:
        result = run_h4_targeted_partial_expansion_validation(config)
    except Exception as exc:
        print(f"H4 targeted partial expansion validation failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4 targeted partial expansion validation completed")
    print(f"Candidate rows: {len(result.candidates)}")
    print(f"Run rows: {len(result.run_summaries)}")
    if summary:
        print(f"Validated partial candidates: {summary.validated_partial_candidate_count}")
        print(f"Readiness flag: {summary.h4_partial_expansion_readiness_flag}")
    print(f"Summary path: {result.research_output_dir / 'h4_targeted_partial_expansion_validation_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
