#!/usr/bin/env python3
"""Run SQRE H4 expanded historical sample feasibility review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.h4_expanded_sample_feasibility_review.config import H4ExpandedSampleFeasibilityConfig
from sqre.h4_expanded_sample_feasibility_review.h4_expanded_sample_feasibility_review_pipeline import (
    run_h4_expanded_sample_feasibility_review,
)


def parse_args() -> argparse.Namespace:
    defaults = H4ExpandedSampleFeasibilityConfig()
    parser = argparse.ArgumentParser(description="Run SQRE H4 expanded historical sample feasibility review")
    parser.add_argument("--sample-config", type=Path, default=defaults.sample_config)
    parser.add_argument("--expanded-validation-config", type=Path, default=defaults.expanded_validation_config)
    parser.add_argument("--h4-d1-validation-config", type=Path, default=defaults.h4_d1_validation_config)
    parser.add_argument("--availability-csv", type=Path, default=defaults.availability_csv)
    parser.add_argument("--master-summary-csv", type=Path, default=defaults.master_summary_csv)
    parser.add_argument("--expanded-summary-csv", type=Path, default=defaults.expanded_summary_csv)
    parser.add_argument("--h4-d1-validation-summary", type=Path, default=defaults.h4_d1_validation_summary)
    parser.add_argument("--h4-d1-research-dir", type=Path, default=defaults.h4_d1_research_dir)
    parser.add_argument("--raw-data-dir", type=Path, default=defaults.raw_data_dir)
    parser.add_argument("--partial-data-dir", type=Path, default=defaults.partial_data_dir)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/research/h4_expanded_sample_feasibility_review"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(
            "data/research/h4_expanded_sample_feasibility_review/"
            "h4_expanded_sample_feasibility_review_report.txt"
        ),
    )
    parser.add_argument("--minimum-full-coverage-ratio", type=float, default=defaults.minimum_full_coverage_ratio)
    parser.add_argument("--minimum-partial-coverage-ratio", type=float, default=defaults.minimum_partial_coverage_ratio)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = H4ExpandedSampleFeasibilityConfig(
        sample_config=args.sample_config,
        expanded_validation_config=args.expanded_validation_config,
        h4_d1_validation_config=args.h4_d1_validation_config,
        availability_csv=args.availability_csv,
        master_summary_csv=args.master_summary_csv,
        expanded_summary_csv=args.expanded_summary_csv,
        h4_d1_validation_summary=args.h4_d1_validation_summary,
        h4_d1_research_dir=args.h4_d1_research_dir,
        raw_data_dir=args.raw_data_dir,
        partial_data_dir=args.partial_data_dir,
        minimum_full_coverage_ratio=args.minimum_full_coverage_ratio,
        minimum_partial_coverage_ratio=args.minimum_partial_coverage_ratio,
    )
    print(f"Output directory: {args.output_dir}")
    print(f"Report: {args.report}")
    try:
        result = run_h4_expanded_sample_feasibility_review(args.output_dir, args.report, config)
    except Exception as exc:
        print(f"H4 expanded sample feasibility review failed: {exc}", file=sys.stderr)
        return 1

    summary = result.summary
    print("H4 expanded sample feasibility review completed")
    print(f"Source inventory rows: {len(result.source_inventory)}")
    print(f"Defined H4 samples: {len(result.defined_samples)}")
    print(f"Raw H4 files: {len(result.raw_files)}")
    print(f"Availability review rows: {len(result.availability_rows)}")
    print(f"Validation coverage rows: {len(result.validation_rows)}")
    print(f"Feasibility matrix rows: {len(result.feasibility_rows)}")
    print(f"Feasible candidate rows: {len(result.feasible_candidates)}")
    print(f"Constrained or missing rows: {len(result.constrained_or_missing_samples)}")
    if summary:
        print(f"Readiness flag: {summary.h4_expansion_readiness_flag}")
        print(f"Dominant constraint class: {summary.dominant_constraint_class}")
    print(f"Summary path: {result.output_dir / 'h4_expanded_sample_feasibility_summary.csv'}")
    print(f"Report path: {result.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
