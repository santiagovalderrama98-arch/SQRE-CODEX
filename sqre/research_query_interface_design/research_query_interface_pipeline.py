"""Pipeline for Research Query Interface Design."""

from __future__ import annotations

from sqre.research_query_interface_design.config import ResearchQueryInterfaceDesignConfig
from sqre.research_query_interface_design.findings import build_summary
from sqre.research_query_interface_design.loader import ResearchQueryInterfaceDesignLoader
from sqre.research_query_interface_design.models import ResearchQueryInterfaceDesignResult
from sqre.research_query_interface_design.query_coverage_review import build_query_coverage_review
from sqre.research_query_interface_design.query_request_builder import build_query_requests
from sqre.research_query_interface_design.query_result_quality_review import (
    build_query_evidence_quality_review,
    build_query_result_quality_review,
)
from sqre.research_query_interface_design.reports import write_outputs
from sqre.research_query_interface_design.research_query_engine import run_research_queries
from sqre.research_query_interface_design.source_inventory import build_source_inventory


class ResearchQueryInterfaceDesignPipeline:
    """Run the research-only query interface design workflow."""

    def __init__(self, config: ResearchQueryInterfaceDesignConfig) -> None:
        self.config = config

    def run(self) -> ResearchQueryInterfaceDesignResult:
        frames = ResearchQueryInterfaceDesignLoader(self.config).load_inputs()
        source_inventory = build_source_inventory(self.config)
        query_requests = build_query_requests(
            frames["usage_scenarios"],
            frames["transition_alignment"],
            frames["reference_store"],
            self.config,
        )
        query_results, fallback_trace = run_research_queries(query_requests, frames["reference_store"], self.config)
        evidence_quality_review = build_query_evidence_quality_review(query_results)
        coverage_review = build_query_coverage_review(query_requests, query_results, self.config)
        result_quality_review = build_query_result_quality_review(query_results)
        summary = build_summary(frames["reference_store"], query_requests, query_results, coverage_review, self.config)
        result = ResearchQueryInterfaceDesignResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            source_inventory=source_inventory,
            query_requests=query_requests,
            query_results=query_results,
            fallback_trace=fallback_trace,
            evidence_quality_review=evidence_quality_review,
            coverage_review=coverage_review,
            result_quality_review=result_quality_review,
            summary=summary,
            **frames,
        )
        return write_outputs(result)

