"""Pipeline for manual research dashboard review."""

from __future__ import annotations

from sqre.manual_research_dashboard_review.config import ManualResearchDashboardReviewConfig
from sqre.manual_research_dashboard_review.field_usefulness_review import build_field_usefulness_review
from sqre.manual_research_dashboard_review.loader import ManualResearchDashboardReviewLoader
from sqre.manual_research_dashboard_review.models import ManualResearchDashboardReviewResult
from sqre.manual_research_dashboard_review.panel_completeness_review import build_panel_completeness_review
from sqre.manual_research_dashboard_review.panel_readability_review import build_panel_readability_review
from sqre.manual_research_dashboard_review.redundancy_review import build_redundancy_review
from sqre.manual_research_dashboard_review.refinement_recommendations import build_refinement_recommendations
from sqre.manual_research_dashboard_review.refined_html_renderer import render_refined_html
from sqre.manual_research_dashboard_review.reports import build_report_text, write_outputs
from sqre.manual_research_dashboard_review.scope_safety_review import build_scope_safety_review
from sqre.manual_research_dashboard_review.source_inventory import build_source_inventory
from sqre.manual_research_dashboard_review.usability_findings import build_summary


class ManualResearchDashboardReviewPipeline:
    """Run dashboard usability review and refined static HTML generation."""

    def __init__(self, config: ManualResearchDashboardReviewConfig) -> None:
        self.config = config

    def run(self) -> ManualResearchDashboardReviewResult:
        loader = ManualResearchDashboardReviewLoader(self.config)
        frames = loader.load_frames()
        texts = loader.load_texts()
        source_inventory = build_source_inventory(self.config)
        panel_completeness = build_panel_completeness_review(frames, texts)
        panel_readability = build_panel_readability_review(frames, texts)
        field_usefulness = build_field_usefulness_review(frames) if self.config.include_field_usefulness_review else _empty()
        redundancy_review = build_redundancy_review(frames) if self.config.include_redundancy_review else _empty()
        scope_safety = build_scope_safety_review(texts) if self.config.include_scope_safety_review else _empty()
        refinement_recommendations = build_refinement_recommendations(
            panel_completeness,
            panel_readability,
            redundancy_review,
            scope_safety,
        )
        summary = build_summary(
            self.config,
            source_inventory,
            panel_completeness,
            panel_readability,
            field_usefulness,
            redundancy_review,
            scope_safety,
            refinement_recommendations,
        )
        result = ManualResearchDashboardReviewResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            html_path=self.config.html_path,
            frames=frames,
            texts=texts,
            source_inventory=source_inventory,
            panel_completeness=panel_completeness,
            panel_readability=panel_readability,
            field_usefulness=field_usefulness,
            redundancy_review=redundancy_review,
            scope_safety=scope_safety,
            refinement_recommendations=refinement_recommendations,
            summary=summary,
        )
        if self.config.include_scope_safety_review:
            generated_texts = {
                **texts,
                "manual_review_report": build_report_text(result),
                "manual_refined_html": render_refined_html(result, self.config.dashboard_title),
            }
            scope_safety = build_scope_safety_review(generated_texts)
            refinement_recommendations = build_refinement_recommendations(
                panel_completeness,
                panel_readability,
                redundancy_review,
                scope_safety,
            )
            summary = build_summary(
                self.config,
                source_inventory,
                panel_completeness,
                panel_readability,
                field_usefulness,
                redundancy_review,
                scope_safety,
                refinement_recommendations,
            )
            result = ManualResearchDashboardReviewResult(
                output_dir=self.config.output_dir,
                report_path=self.config.report_path,
                html_path=self.config.html_path,
                frames=frames,
                texts=texts,
                source_inventory=source_inventory,
                panel_completeness=panel_completeness,
                panel_readability=panel_readability,
                field_usefulness=field_usefulness,
                redundancy_review=redundancy_review,
                scope_safety=scope_safety,
                refinement_recommendations=refinement_recommendations,
                summary=summary,
            )
        return write_outputs(result, self.config.dashboard_title)


def _empty():
    import pandas as pd

    return pd.DataFrame()
