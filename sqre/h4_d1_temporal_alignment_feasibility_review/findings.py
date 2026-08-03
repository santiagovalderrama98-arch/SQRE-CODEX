"""Descriptive findings for H4/D1 temporal alignment feasibility review."""

from __future__ import annotations

from sqre.h4_d1_temporal_alignment_feasibility_review.models import TemporalAlignmentFeasibilitySummary


def descriptive_findings(summary: TemporalAlignmentFeasibilitySummary | None) -> list[str]:
    if summary is None:
        return ["No feasibility summary row was produced."]
    return [
        "This review checks feasibility only.",
        "This review does not perform H4/D1 contextual interpretation.",
        "This review does not use condition-level matching as same-time alignment.",
        "Same-time H4/D1 alignment requires timestamp, interval, or scenario-period keys.",
        "If H4 combined context lacks timestamp/scenario/date fields, it is not ready for same-time H4/D1 alignment.",
        f"Dominant alignment feasibility class: {summary.dominant_alignment_feasibility_class}",
        f"Temporal alignment readiness flag: {summary.temporal_alignment_readiness_flag}",
        f"Temporal alignment diagnostic: {summary.temporal_alignment_diagnostic}",
        f"Recommended follow-up: {summary.recommended_follow_up}",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "Generate H4 timestamped context table",
        "Generate D1 timestamped regime/state table",
        "Build H4/D1 interval overlap alignment table",
        "Review scenario-period mapping completeness",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No data was downloaded.",
        "No provider behavior was changed.",
        "No same-time H4/D1 interpretation was produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Feasibility only.",
        "Findings depend on local files currently present in workspace.",
        "Existing H4 combined context may be condition-level only.",
        "Existing D1 profiles may be aggregate/regime-level only.",
        "No operational decision is produced.",
    ]
