"""Pipeline for SQRE reference stability documentation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.dashboard_reading_guide_builder import build_dashboard_reading_guide
from sqre.reference_stability_documentation.evidence_usage_policy_builder import build_evidence_usage_policy
from sqre.reference_stability_documentation.findings import build_summary, scope_statements
from sqre.reference_stability_documentation.follow_up_documentation_builder import build_follow_up_plan
from sqre.reference_stability_documentation.limitation_documentation_builder import build_limitations_documentation
from sqre.reference_stability_documentation.loader import ReferenceStabilityDocumentationLoader
from sqre.reference_stability_documentation.markdown_renderer import render_markdown
from sqre.reference_stability_documentation.models import ReferenceStabilityDocumentationResult
from sqre.reference_stability_documentation.reports import build_report_text, write_outputs
from sqre.reference_stability_documentation.scope_safety_review import build_scope_safety_review
from sqre.reference_stability_documentation.source_inventory import build_source_inventory
from sqre.reference_stability_documentation.stability_interpretation_builder import build_stability_interpretation_guide


class ReferenceStabilityDocumentationPipeline:
    """Run reference stability documentation and write research-only outputs."""

    def __init__(self, config: ReferenceStabilityDocumentationConfig) -> None:
        self.config = config

    def run(self) -> ReferenceStabilityDocumentationResult:
        loader = ReferenceStabilityDocumentationLoader(self.config)
        frames = loader.load_frames()
        texts = loader.load_texts()
        source_inventory = build_source_inventory(self.config)
        interpretation = build_stability_interpretation_guide(_frame(frames, "reference_stability_scorecard"))
        usage_policy = build_evidence_usage_policy(_frame(frames, "reference_stability_validation_summary"))
        dashboard_guide = build_dashboard_reading_guide(
            self.config.include_dashboard_reading_guide,
            _frame(frames, "research_dashboard_reference_cards"),
        )
        limitations = build_limitations_documentation()
        follow_up = build_follow_up_plan(self.config.include_follow_up_plan)

        scope_review = build_scope_safety_review(
            self.config.include_scope_safety_review,
            _scope_sources(texts, interpretation, usage_policy, dashboard_guide, limitations, follow_up),
        )
        summary = build_summary(
            self.config,
            source_inventory,
            interpretation,
            usage_policy,
            dashboard_guide,
            limitations,
            follow_up,
            scope_review,
        )
        result = ReferenceStabilityDocumentationResult(
            output_dir=self.config.output_dir,
            report_path=self.config.report_path,
            markdown_path=self.config.markdown_path,
            config=self.config,
            frames=frames,
            texts=texts,
            source_inventory=source_inventory,
            interpretation_guide=interpretation,
            evidence_usage_policy=usage_policy,
            dashboard_reading_guide=dashboard_guide,
            limitations_documentation=limitations,
            follow_up_plan=follow_up,
            scope_safety_review=scope_review,
            summary=summary,
        )
        rendered_markdown = render_markdown(
            self.config,
            interpretation,
            usage_policy,
            dashboard_guide,
            limitations,
            follow_up,
            summary,
        )
        preview_result = ReferenceStabilityDocumentationResult(
            output_dir=result.output_dir,
            report_path=result.report_path,
            markdown_path=result.markdown_path,
            config=self.config,
            source_inventory=source_inventory,
            interpretation_guide=interpretation,
            evidence_usage_policy=usage_policy,
            dashboard_reading_guide=dashboard_guide,
            limitations_documentation=limitations,
            follow_up_plan=follow_up,
            scope_safety_review=scope_review,
            summary=summary,
        )
        final_scope = build_scope_safety_review(
            self.config.include_scope_safety_review,
            {"report": build_report_text(preview_result), "markdown": rendered_markdown},
        )
        summary = build_summary(
            self.config,
            source_inventory,
            interpretation,
            usage_policy,
            dashboard_guide,
            limitations,
            follow_up,
            final_scope,
        )
        return write_outputs(
            ReferenceStabilityDocumentationResult(
                output_dir=self.config.output_dir,
                report_path=self.config.report_path,
                markdown_path=self.config.markdown_path,
                config=self.config,
                frames=frames,
                texts=texts,
                source_inventory=source_inventory,
                interpretation_guide=interpretation,
                evidence_usage_policy=usage_policy,
                dashboard_reading_guide=dashboard_guide,
                limitations_documentation=limitations,
                follow_up_plan=follow_up,
                scope_safety_review=final_scope,
                summary=summary,
            )
        )


def _scope_sources(
    texts: dict[str, str],
    interpretation,
    usage_policy,
    dashboard_guide,
    limitations,
    follow_up,
) -> dict[str, str]:
    sources = dict(texts)
    sources["interpretation_guide"] = interpretation.to_csv(index=False)
    sources["evidence_usage_policy"] = usage_policy.to_csv(index=False)
    sources["dashboard_reading_guide"] = dashboard_guide.to_csv(index=False)
    sources["limitations_documentation"] = limitations.to_csv(index=False)
    sources["follow_up_plan"] = follow_up.to_csv(index=False)
    sources["scope_statements"] = "\n".join(scope_statements())
    return sources


def _frame(frames: dict[str, pd.DataFrame], name: str) -> pd.DataFrame:
    return frames.get(name, pd.DataFrame())
