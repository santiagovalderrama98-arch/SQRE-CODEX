"""Summary classification for H4/D1 temporal alignment feasibility."""

from __future__ import annotations

from collections import Counter

from sqre.h4_d1_temporal_alignment_feasibility_review.config import H4D1TemporalAlignmentFeasibilityConfig
from sqre.h4_d1_temporal_alignment_feasibility_review.models import (
    AlignmentCandidateReviewRow,
    SourceInventoryRow,
    TemporalAlignmentFeasibilitySummary,
    TemporalKeyInventoryRow,
)
from sqre.h4_d1_temporal_alignment_feasibility_review.temporal_key_inventory import (
    has_condition_only,
    has_exact_timestamp,
    has_scenario_period,
    has_start_end,
)


def build_summary(
    sources: list[SourceInventoryRow],
    keys: list[TemporalKeyInventoryRow],
    candidates: list[AlignmentCandidateReviewRow],
    config: H4D1TemporalAlignmentFeasibilityConfig,
) -> TemporalAlignmentFeasibilitySummary:
    feasibility_counts = Counter(row.alignment_feasibility_class for row in candidates)
    dominant = _dominant_feasibility(feasibility_counts)
    h4_status = _side_status([row for row in keys if row.source_type == "H4_COMBINED_CONTEXT"])
    d1_status = _side_status([row for row in keys if row.source_type.startswith("D1")])
    flag = _readiness_flag(dominant, h4_status, d1_status)
    return TemporalAlignmentFeasibilitySummary(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        source_count=len(sources),
        loaded_source_count=sum(1 for row in sources if row.load_status == "LOADED"),
        h4_source_count=sum(1 for row in sources if row.source_type == "H4_COMBINED_CONTEXT"),
        d1_source_count=sum(1 for row in sources if row.source_type.startswith("D1")),
        sources_with_exact_timestamp_count=sum(1 for row in keys if has_exact_timestamp(row)),
        sources_with_start_end_time_count=sum(1 for row in keys if has_start_end(row)),
        sources_with_scenario_period_key_count=sum(1 for row in keys if has_scenario_period(row)),
        sources_with_condition_only_key_count=sum(1 for row in keys if has_condition_only(row)),
        h4_temporal_key_status=h4_status,
        d1_temporal_key_status=d1_status,
        candidate_count=len(candidates),
        ready_exact_timestamp_candidate_count=feasibility_counts["READY_FOR_EXACT_TIMESTAMP_ALIGNMENT"],
        ready_interval_overlap_candidate_count=feasibility_counts["READY_FOR_INTERVAL_OVERLAP_ALIGNMENT"],
        ready_scenario_period_candidate_count=feasibility_counts["READY_FOR_SCENARIO_PERIOD_ALIGNMENT"],
        condition_only_not_temporal_candidate_count=feasibility_counts["CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT"],
        input_limited_candidate_count=feasibility_counts["INPUT_LIMITED"],
        dominant_alignment_feasibility_class=dominant,
        temporal_alignment_readiness_flag=flag,
        temporal_alignment_diagnostic=_diagnostic(flag),
        recommended_follow_up=_follow_up(flag),
    )


def _side_status(rows: list[TemporalKeyInventoryRow]) -> str:
    statuses = [row.temporal_key_status for row in rows]
    if not statuses or all(status == "INPUT_MISSING" for status in statuses):
        return "INPUT_MISSING"
    for status in [
        "EXACT_TIMESTAMP_KEYS_AVAILABLE",
        "SCENARIO_PERIOD_KEYS_AVAILABLE",
        "START_END_TIME_KEYS_AVAILABLE",
        "DATE_RANGE_KEYS_AVAILABLE",
    ]:
        if status in statuses:
            return status
    if "CONDITION_ONLY_KEYS_AVAILABLE" in statuses:
        return "CONDITION_ONLY_KEYS_AVAILABLE"
    return "TEMPORAL_KEYS_MISSING"


def _dominant_feasibility(counter: Counter[str]) -> str:
    if not counter:
        return "INPUT_LIMITED"
    priority = {
        "READY_FOR_EXACT_TIMESTAMP_ALIGNMENT": 0,
        "READY_FOR_INTERVAL_OVERLAP_ALIGNMENT": 1,
        "READY_FOR_SCENARIO_PERIOD_ALIGNMENT": 2,
        "CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT": 3,
        "NOT_READY_MISSING_H4_TEMPORAL_KEYS": 4,
        "NOT_READY_MISSING_D1_TEMPORAL_KEYS": 5,
        "NOT_READY_MISSING_BOTH_TEMPORAL_KEYS": 6,
        "INPUT_LIMITED": 7,
    }
    return sorted(counter.items(), key=lambda item: (priority.get(item[0], 99), -item[1], item[0]))[0][0]


def _readiness_flag(dominant: str, h4_status: str, d1_status: str) -> str:
    if dominant in {"READY_FOR_EXACT_TIMESTAMP_ALIGNMENT", "READY_FOR_INTERVAL_OVERLAP_ALIGNMENT"}:
        return "READY_FOR_SAME_TIME_H4_D1_ALIGNMENT"
    if dominant == "READY_FOR_SCENARIO_PERIOD_ALIGNMENT":
        return "READY_FOR_SCENARIO_PERIOD_H4_D1_ALIGNMENT"
    if dominant == "CONDITION_ONLY_NOT_TEMPORAL_ALIGNMENT":
        return "CONDITION_LEVEL_ONLY_NOT_TEMPORAL_ALIGNMENT"
    if dominant == "NOT_READY_MISSING_H4_TEMPORAL_KEYS":
        return "NOT_READY_H4_CONTEXT_TEMPORAL_KEYS_MISSING"
    if dominant == "NOT_READY_MISSING_D1_TEMPORAL_KEYS":
        return "NOT_READY_D1_CONTEXT_TEMPORAL_KEYS_MISSING"
    if dominant == "NOT_READY_MISSING_BOTH_TEMPORAL_KEYS":
        if h4_status == "CONDITION_ONLY_KEYS_AVAILABLE" or d1_status == "CONDITION_ONLY_KEYS_AVAILABLE":
            return "CONDITION_LEVEL_ONLY_NOT_TEMPORAL_ALIGNMENT"
        return "NOT_READY_BOTH_TEMPORAL_KEYS_MISSING"
    return "INPUT_COMPLETENESS_REVIEW_REQUIRED"


def _diagnostic(flag: str) -> str:
    diagnostics = {
        "READY_FOR_SAME_TIME_H4_D1_ALIGNMENT": "Timestamp or interval keys are available for same-time H4/D1 alignment review.",
        "READY_FOR_SCENARIO_PERIOD_H4_D1_ALIGNMENT": "Scenario-period keys are available for H4/D1 alignment review.",
        "NOT_READY_H4_CONTEXT_TEMPORAL_KEYS_MISSING": "H4 combined context lacks timestamp, interval, or scenario-period keys.",
        "NOT_READY_D1_CONTEXT_TEMPORAL_KEYS_MISSING": "D1 context lacks timestamp, interval, or scenario-period keys.",
        "NOT_READY_BOTH_TEMPORAL_KEYS_MISSING": "Both H4 and D1 sources lack same-time temporal alignment keys.",
        "CONDITION_LEVEL_ONLY_NOT_TEMPORAL_ALIGNMENT": (
            "Available keys support condition-level matching only; this is not same-time temporal alignment."
        ),
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "Source completeness must be reviewed before temporal alignment feasibility can be assessed.",
    }
    return diagnostics[flag]


def _follow_up(flag: str) -> str:
    mapping = {
        "READY_FOR_SAME_TIME_H4_D1_ALIGNMENT": "Build H4/D1 interval overlap alignment table",
        "READY_FOR_SCENARIO_PERIOD_H4_D1_ALIGNMENT": "Review scenario-period mapping completeness",
        "NOT_READY_H4_CONTEXT_TEMPORAL_KEYS_MISSING": "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE",
        "NOT_READY_D1_CONTEXT_TEMPORAL_KEYS_MISSING": "GENERATE_D1_TIMESTAMPED_REGIME_TABLE",
        "NOT_READY_BOTH_TEMPORAL_KEYS_MISSING": "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE; GENERATE_D1_TIMESTAMPED_REGIME_TABLE",
        "CONDITION_LEVEL_ONLY_NOT_TEMPORAL_ALIGNMENT": "GENERATE_H4_TIMESTAMPED_CONTEXT_TABLE",
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "REVIEW_SOURCE_INPUT_COMPLETENESS",
    }
    return mapping[flag]
