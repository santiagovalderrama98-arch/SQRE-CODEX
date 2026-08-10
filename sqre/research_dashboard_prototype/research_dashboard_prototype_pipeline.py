"""Pipeline for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from sqre.research_dashboard_prototype.behavior_panel_builder import build_behavior_panel
from sqre.research_dashboard_prototype.config import ResearchDashboardPrototypeConfig
from sqre.research_dashboard_prototype.diagnostic_panel_builder import build_diagnostic_panel
from sqre.research_dashboard_prototype.evidence_panel_builder import build_evidence_panel
from sqre.research_dashboard_prototype.fallback_panel_builder import build_fallback_panel
from sqre.research_dashboard_prototype.findings import build_summary
from sqre.research_dashboard_prototype.loader import ResearchDashboardPrototypeLoader
from sqre.research_dashboard_prototype.models import ResearchDashboardPrototypeResult
from sqre.research_dashboard_prototype.reference_panel_builder import build_reference_cards
from sqre.research_dashboard_prototype.reports import write_outputs
from sqre.research_dashboard_prototype.snapshot_panel_builder import build_snapshot_panel
from sqre.research_dashboard_prototype.source_inventory import build_source_inventory


class ResearchDashboardPrototypePipeline:
    """Run the research-only static dashboard prototype workflow."""

    def __init__(self, config: ResearchDashboardPrototypeConfig) -> None:
        self.config = config

    def run(self) -> ResearchDashboardPrototypeResult:
        frames = ResearchDashboardPrototypeLoader(self.config).load_inputs()
        source_inventory = build_source_inventory(self.config)
        snapshot_panel = build_snapshot_panel(frames, self.config)
        reference_cards = build_reference_cards(frames, self.config)
        evidence_panel = build_evidence_panel(frames)
        behavior_panel = build_behavior_panel(frames)
        fallback_panel = build_fallback_panel(frames, self.config)
        diagnostic_panel = build_diagnostic_panel(frames)
        summary = build_summary(
            frames,
            source_inventory,
            reference_cards,
            evidence_panel,
            behavior_panel,
            fallback_panel,
            diagnostic_panel,
            self.config,
        )
        result = ResearchDashboardPrototypeResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            html_path=self.config.html_path,
            source_inventory=source_inventory,
            frames=frames,
            snapshot_panel=snapshot_panel,
            reference_cards=reference_cards,
            evidence_panel=evidence_panel,
            behavior_panel=behavior_panel,
            fallback_panel=fallback_panel,
            diagnostic_panel=diagnostic_panel,
            summary=summary,
        )
        return write_outputs(result, self.config.dashboard_title)
