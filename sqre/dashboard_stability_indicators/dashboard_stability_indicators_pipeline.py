"""Pipeline for SQRE dashboard stability indicators."""

from __future__ import annotations

import logging

from sqre.dashboard_stability_indicators.behavior_panel_indicator_builder import build_behavior_stability_panel
from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.dashboard_warning_builder import build_dashboard_warning_summary
from sqre.dashboard_stability_indicators.evidence_panel_indicator_builder import build_evidence_stability_panel
from sqre.dashboard_stability_indicators.fallback_indicator_builder import build_fallback_stability_panel
from sqre.dashboard_stability_indicators.findings import build_summary
from sqre.dashboard_stability_indicators.indicator_html_renderer import render_html
from sqre.dashboard_stability_indicators.loader import DashboardStabilityIndicatorsLoader
from sqre.dashboard_stability_indicators.models import DashboardStabilityIndicatorsResult
from sqre.dashboard_stability_indicators.reference_card_indicator_builder import build_reference_card_indicators
from sqre.dashboard_stability_indicators.reports import build_report_text, write_outputs
from sqre.dashboard_stability_indicators.scope_safety_review import build_scope_safety_review
from sqre.dashboard_stability_indicators.source_inventory import build_source_inventory
from sqre.dashboard_stability_indicators.stability_indicator_legend_builder import build_stability_indicator_legend
from sqre.dashboard_stability_indicators.stability_indicator_mapper import build_stability_indicator_map


logger = logging.getLogger(__name__)


class DashboardStabilityIndicatorsPipeline:
    """Run the dashboard stability indicator workflow."""

    def __init__(self, config: DashboardStabilityIndicatorsConfig) -> None:
        self.config = config

    def run(self) -> DashboardStabilityIndicatorsResult:
        logger.info("Running dashboard stability indicators")
        loader = DashboardStabilityIndicatorsLoader(self.config)
        frames = loader.load_frames()
        texts = loader.load_texts()
        source_inventory = build_source_inventory(self.config)
        legend = build_stability_indicator_legend(self.config.include_stability_legend)
        indicator_map = build_stability_indicator_map(frames.get("interpretation_guide"))
        reference_cards = build_reference_card_indicators(self.config, frames.get("reference_cards"))
        evidence_panel = build_evidence_stability_panel(reference_cards, frames.get("evidence_panel"))
        behavior_panel = build_behavior_stability_panel(reference_cards, frames.get("behavior_panel"))
        fallback_panel = build_fallback_stability_panel(self.config, frames.get("fallback_panel"))
        warning_summary = build_dashboard_warning_summary(reference_cards, fallback_panel)
        preliminary = DashboardStabilityIndicatorsResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            html_path=self.config.html_path,
            config=self.config,
            frames=frames,
            texts=texts,
            source_inventory=source_inventory,
            indicator_legend=legend,
            indicator_map=indicator_map,
            reference_card_indicators=reference_cards,
            evidence_panel=evidence_panel,
            behavior_panel=behavior_panel,
            fallback_panel=fallback_panel,
            warning_summary=warning_summary,
        )
        preliminary_summary = build_summary(
            self.config,
            source_inventory,
            indicator_map,
            reference_cards,
            warning_summary,
            build_scope_safety_review(False, {}),
        )
        preliminary = DashboardStabilityIndicatorsResult(**{**preliminary.__dict__, "summary": preliminary_summary})
        report_preview = build_report_text(preliminary)
        html_preview = render_html(
            self.config,
            preliminary_summary,
            legend,
            reference_cards,
            evidence_panel,
            behavior_panel,
            fallback_panel,
            warning_summary,
        )
        scope_review = build_scope_safety_review(
            self.config.include_scope_safety_review,
            {"dashboard_stability_indicators_report.txt": report_preview, "dashboard_stability_indicators.html": html_preview},
        )
        summary = build_summary(self.config, source_inventory, indicator_map, reference_cards, warning_summary, scope_review)
        result = DashboardStabilityIndicatorsResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            html_path=self.config.html_path,
            config=self.config,
            frames=frames,
            texts=texts,
            source_inventory=source_inventory,
            indicator_legend=legend,
            indicator_map=indicator_map,
            reference_card_indicators=reference_cards,
            evidence_panel=evidence_panel,
            behavior_panel=behavior_panel,
            fallback_panel=fallback_panel,
            warning_summary=warning_summary,
            scope_safety_review=scope_review,
            summary=summary,
        )
        return write_outputs(result)
