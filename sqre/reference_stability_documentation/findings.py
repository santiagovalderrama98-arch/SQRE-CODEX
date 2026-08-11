"""Findings and readiness assessment for reference stability documentation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.models import ReferenceStabilityDocumentationSummary, class_count
from sqre.reference_stability_documentation.scope_safety_review import scope_safety_class
from sqre.reference_stability_documentation.source_inventory import has_missing_required_inputs


def build_summary(
    config: ReferenceStabilityDocumentationConfig,
    source_inventory: list[object],
    interpretation: pd.DataFrame,
    usage_policy: pd.DataFrame,
    dashboard_guide: pd.DataFrame,
    limitations: pd.DataFrame,
    follow_up: pd.DataFrame,
    scope_review: pd.DataFrame,
) -> ReferenceStabilityDocumentationSummary:
    scope_class = scope_safety_class(scope_review)
    scope_warnings = class_count(scope_review, "Documentation_Scope_Safety_Class", "DOCUMENTATION_SCOPE_WARNING")
    scope_violations = class_count(scope_review, "Documentation_Scope_Safety_Class", "DOCUMENTATION_SCOPE_VIOLATION")
    readiness_class, readiness_flag, diagnostic = _readiness(
        missing_required=has_missing_required_inputs(source_inventory),
        scope_class=scope_class,
        stable_count=class_count(interpretation, "Documentation_Class", "DOCUMENTED_STABLE_EVIDENCE"),
        partial_count=class_count(interpretation, "Documentation_Class", "DOCUMENTED_PARTIAL_EVIDENCE"),
        guide_count=len(dashboard_guide),
        limitation_count=len(limitations),
    )
    return ReferenceStabilityDocumentationSummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        stability_dimension_count=len(interpretation),
        documented_stable_evidence_count=class_count(interpretation, "Documentation_Class", "DOCUMENTED_STABLE_EVIDENCE"),
        documented_partial_evidence_count=class_count(interpretation, "Documentation_Class", "DOCUMENTED_PARTIAL_EVIDENCE"),
        documented_constrained_evidence_count=class_count(interpretation, "Documentation_Class", "DOCUMENTED_CONSTRAINED_EVIDENCE"),
        documented_unstable_evidence_count=class_count(interpretation, "Documentation_Class", "DOCUMENTED_UNSTABLE_EVIDENCE"),
        safe_for_manual_research_review_count=class_count(usage_policy, "Evidence_Usage_Policy_Class", "SAFE_FOR_MANUAL_RESEARCH_REVIEW"),
        use_with_stability_warnings_count=class_count(usage_policy, "Evidence_Usage_Policy_Class", "USE_WITH_STABILITY_WARNINGS"),
        documentation_only_count=class_count(usage_policy, "Evidence_Usage_Policy_Class", "DOCUMENTATION_ONLY"),
        dashboard_guide_element_count=len(dashboard_guide),
        limitation_count=len(limitations),
        follow_up_count=len(follow_up),
        high_priority_follow_up_count=class_count(follow_up, "Follow_Up_Priority", "HIGH"),
        medium_priority_follow_up_count=class_count(follow_up, "Follow_Up_Priority", "MEDIUM"),
        low_priority_follow_up_count=class_count(follow_up, "Follow_Up_Priority", "LOW"),
        documentation_scope_safety_class=scope_class,
        scope_warning_count=scope_warnings,
        scope_violation_count=scope_violations,
        reference_stability_documentation_readiness_class=readiness_class,
        reference_stability_documentation_readiness_flag=readiness_flag,
        reference_stability_documentation_diagnostic=diagnostic,
        recommended_follow_up=recommended_follow_up(readiness_flag),
    )


def potential_follow_up_areas() -> list[str]:
    return [
        "Dashboard stability indicators",
        "Expanded H4 historical data coverage",
        "Multi-pair reference stability replication",
        "Directional consistency review",
        "Fallback dependency review",
        "Live data snapshot integration design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No provider behavior was changed.",
        "No trading signals were produced.",
        "No operational recommendations were produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on local stability validation outputs.",
        "H4 source sample may be partial due to provider row limits.",
        "Stability documentation is interpretive and research-only.",
        "Stable evidence groups do not imply predictive edge.",
        "Dashboard reference cards depend on the latest available snapshot.",
        "No operational decision is produced.",
    ]


def scope_statements() -> list[str]:
    return [
        "This phase documents reference stability for manual research review.",
        "This phase converts stability diagnostics into interpretation guidance.",
        "This phase does not generate trading signals.",
        "This phase does not generate operational recommendations.",
        "This phase does not decide whether any context is favorable or unfavorable.",
        "This phase does not perform profitability analysis.",
        "This phase does not create a Decision Engine.",
        "Documentation findings are descriptive research guidance only.",
        "Later phases may add dashboard stability indicators or extend historical coverage, but this phase does not create production decision logic.",
    ]


def recommended_follow_up(readiness_flag: str) -> str:
    if readiness_flag == "READY_FOR_DASHBOARD_STABILITY_INDICATORS":
        return "Dashboard stability indicators; Expanded H4 historical data coverage"
    if readiness_flag == "PARTIAL_READY_FOR_DASHBOARD_STABILITY_INDICATORS":
        return "Dashboard stability indicators; Directional consistency review; Fallback dependency review"
    if readiness_flag == "NOT_READY_DOCUMENTATION_INPUT_LIMITED":
        return "Input completeness review; Reference stability validation rerun"
    return "Input completeness review"


def _readiness(
    missing_required: bool,
    scope_class: str,
    stable_count: int,
    partial_count: int,
    guide_count: int,
    limitation_count: int,
) -> tuple[str, str, str]:
    if missing_required:
        return "INPUT_MISSING", "INPUT_COMPLETENESS_REVIEW_REQUIRED", "Required stability validation inputs are missing."
    if scope_class == "DOCUMENTATION_SCOPE_VIOLATION":
        return (
            "REFERENCE_STABILITY_DOCUMENTATION_INPUT_LIMITED",
            "NOT_READY_DOCUMENTATION_INPUT_LIMITED",
            "Documentation contains unsafe scope language.",
        )
    if stable_count >= 4 and guide_count > 0 and limitation_count > 0:
        return (
            "REFERENCE_STABILITY_DOCUMENTATION_READY",
            "READY_FOR_DASHBOARD_STABILITY_INDICATORS",
            "Reference stability documentation is ready for dashboard stability indicator design.",
        )
    if partial_count > 0 and guide_count > 0:
        return (
            "PARTIAL_REFERENCE_STABILITY_DOCUMENTATION_READY",
            "PARTIAL_READY_FOR_DASHBOARD_STABILITY_INDICATORS",
            "Reference stability documentation is ready with explicit partial evidence cautions.",
        )
    return (
        "REFERENCE_STABILITY_DOCUMENTATION_INPUT_LIMITED",
        "NOT_READY_DOCUMENTATION_INPUT_LIMITED",
        "Reference stability documentation has limited input or output coverage.",
    )
