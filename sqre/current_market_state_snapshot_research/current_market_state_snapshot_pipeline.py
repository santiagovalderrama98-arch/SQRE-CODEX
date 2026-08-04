"""Pipeline for Current Market State Snapshot Research."""

from __future__ import annotations

from sqre.current_market_state_snapshot_research.config import CurrentMarketStateSnapshotResearchConfig
from sqre.current_market_state_snapshot_research.findings import build_summary
from sqre.current_market_state_snapshot_research.loader import CurrentMarketStateSnapshotResearchLoader
from sqre.current_market_state_snapshot_research.models import CurrentMarketStateSnapshotResearchResult
from sqre.current_market_state_snapshot_research.reports import write_outputs
from sqre.current_market_state_snapshot_research.snapshot_behavior_summary import build_snapshot_behavior_summary
from sqre.current_market_state_snapshot_research.snapshot_context_builder import build_snapshot_context
from sqre.current_market_state_snapshot_research.snapshot_diagnostic_review import build_snapshot_diagnostic_review
from sqre.current_market_state_snapshot_research.snapshot_evidence_review import build_snapshot_evidence_review
from sqre.current_market_state_snapshot_research.snapshot_query_builder import build_snapshot_query_requests
from sqre.current_market_state_snapshot_research.snapshot_reference_lookup import lookup_snapshot_references
from sqre.current_market_state_snapshot_research.source_inventory import build_source_inventory


class CurrentMarketStateSnapshotResearchPipeline:
    """Run the research-only current market state snapshot workflow."""

    def __init__(self, config: CurrentMarketStateSnapshotResearchConfig) -> None:
        self.config = config

    def run(self) -> CurrentMarketStateSnapshotResearchResult:
        frames = CurrentMarketStateSnapshotResearchLoader(self.config).load_inputs()
        source_inventory = build_source_inventory(self.config)
        snapshot_context = build_snapshot_context(frames, self.config)
        snapshot_queries = build_snapshot_query_requests(snapshot_context, self.config)
        snapshot_results, fallback_trace = lookup_snapshot_references(
            snapshot_queries,
            frames["reference_store"],
            self.config,
        )
        evidence_review = build_snapshot_evidence_review(snapshot_results)
        behavior_summary = build_snapshot_behavior_summary(snapshot_queries, snapshot_results)
        diagnostic_review = build_snapshot_diagnostic_review(snapshot_context, snapshot_queries, snapshot_results, fallback_trace)
        summary = build_summary(frames["reference_store"], snapshot_context, snapshot_queries, snapshot_results, self.config)
        result = CurrentMarketStateSnapshotResearchResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=source_inventory,
            snapshot_context=snapshot_context,
            snapshot_query_requests=snapshot_queries,
            snapshot_reference_results=snapshot_results,
            snapshot_fallback_trace=fallback_trace,
            snapshot_evidence_review=evidence_review,
            snapshot_behavior_summary=behavior_summary,
            snapshot_diagnostic_review=diagnostic_review,
            summary=summary,
            **frames,
        )
        return write_outputs(result)
