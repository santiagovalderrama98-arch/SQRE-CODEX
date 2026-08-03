"""Pipeline for Phase 7.5.14A H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from sqre.h4_d1_temporal_alignment_feasibility_review.alignment_candidate_review import (
    build_alignment_candidate_review,
)
from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.feasibility_classifier import build_summary
from sqre.h4_d1_temporal_alignment_feasibility_review.missing_key_review import build_missing_key_review
from sqre.h4_d1_temporal_alignment_feasibility_review.models import TemporalAlignmentFeasibilityResult
from sqre.h4_d1_temporal_alignment_feasibility_review.reports import write_review_outputs
from sqre.h4_d1_temporal_alignment_feasibility_review.source_inventory import build_source_inventory
from sqre.h4_d1_temporal_alignment_feasibility_review.temporal_key_inventory import build_temporal_key_inventory


def run_h4_d1_temporal_alignment_feasibility_review(
    config: H4D1TemporalAlignmentFeasibilityConfig | None = None,
) -> TemporalAlignmentFeasibilityResult:
    active_config = config or H4D1TemporalAlignmentFeasibilityConfig()
    source_inventory = build_source_inventory(active_config)
    temporal_keys = build_temporal_key_inventory(source_inventory)
    candidates = build_alignment_candidate_review(temporal_keys)
    missing_keys = build_missing_key_review(temporal_keys)
    summary = build_summary(source_inventory, temporal_keys, candidates, active_config)
    result = TemporalAlignmentFeasibilityResult(
        output_dir=active_config.output_dir,
        report_path=active_config.report_path,
        source_inventory=source_inventory,
        temporal_key_inventory=temporal_keys,
        alignment_candidates=candidates,
        missing_keys=missing_keys,
        summary=summary,
    )
    return write_review_outputs(result)
