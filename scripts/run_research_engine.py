#!/usr/bin/env python3
"""Run SQRE Phase 7.1 Research Engine."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqre.research_engine import ResearchEngineConfig, run_research_engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQRE research engine")
    parser.add_argument("--states", required=True, help="Input market states CSV path")
    parser.add_argument("--transitions", required=True, help="Input state transitions CSV path")
    parser.add_argument("--output-dir", required=True, help="Output directory for research CSV files")
    parser.add_argument("--report", required=True, help="Output research report path")
    parser.add_argument("--forward-windows", default="1,2,3")
    parser.add_argument("--minimum-sample-size", type=int, default=5)
    parser.add_argument("--sequence-length", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config = ResearchEngineConfig(
        forward_windows=_parse_forward_windows(args.forward_windows),
        minimum_sample_size=args.minimum_sample_size,
        sequence_length=args.sequence_length,
    )

    try:
        summary = run_research_engine(
            states_path=args.states,
            transitions_path=args.transitions,
            output_dir=args.output_dir,
            report_path=args.report,
            config=config,
        )
    except Exception as exc:
        logging.exception("Research engine failed")
        print(f"Research engine failed: {exc}")
        return 1

    print("Research engine completed")
    print(f"States processed: {summary.states_processed}")
    print(f"Transitions processed: {summary.transitions_processed}")
    print(f"Conditions evaluated: {summary.conditions_evaluated}")
    print(f"Forward state rows: {summary.forward_state_rows}")
    print(f"Forward transition rows: {summary.forward_transition_rows}")
    print(f"Preceding state rows: {summary.preceding_state_rows}")
    print(f"Sequence outcome rows: {summary.sequence_outcome_rows}")
    print(f"Condition summary rows: {summary.condition_summary_rows}")
    print(f"Forward state distributions path: {summary.forward_state_distributions_path}")
    print(f"Forward transition distributions path: {summary.forward_transition_distributions_path}")
    print(f"Preceding state distributions path: {summary.preceding_state_distributions_path}")
    print(f"Sequence outcomes path: {summary.sequence_outcomes_path}")
    print(f"Condition summaries path: {summary.condition_summaries_path}")
    print(f"Report path: {summary.report_path}")
    return 0


def _parse_forward_windows(value: str) -> list[int]:
    windows = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not windows:
        raise ValueError("--forward-windows must include at least one integer")
    if any(window <= 0 for window in windows):
        raise ValueError("--forward-windows values must be greater than zero")
    return windows


if __name__ == "__main__":
    raise SystemExit(main())
