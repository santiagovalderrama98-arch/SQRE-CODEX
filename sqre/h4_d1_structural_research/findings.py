"""Findings and timeframe summaries for H4/D1 structural research."""

from __future__ import annotations

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.consistency import cv, mean, mode, ratio, sensitivity_flag
from sqre.h4_d1_structural_research.models import (
    H4D1ResearchFinding,
    PriceOutcomeProfile,
    ScenarioInventoryRow,
    SequenceResearchProfile,
    StateResearchProfile,
    TimeframeResearchSummary,
    TransitionResearchProfile,
)


COMPLETED_STATUSES = {"COMPLETED", "SKIPPED"}


def build_timeframe_summaries(
    inventory_rows: list[ScenarioInventoryRow],
    state_profiles: list[StateResearchProfile],
    transition_profiles: list[TransitionResearchProfile],
    price_profiles: list[PriceOutcomeProfile],
    sequence_profiles: list[SequenceResearchProfile],
    config: H4D1StructuralResearchConfig,
) -> list[TimeframeResearchSummary]:
    summaries: list[TimeframeResearchSummary] = []
    for timeframe in ["H4", "D1"]:
        rows = [row for row in inventory_rows if row.timeframe == timeframe]
        if not rows:
            continue
        structures = [row.structures_detected for row in rows]
        forward_ranges = [row.average_forward_range_pips for row in rows]
        low_research = [row.low_sample_conditions_research for row in rows]
        low_price = [row.low_sample_conditions_price_outcome for row in rows]
        state_count = len([row for row in state_profiles if row.timeframe == timeframe])
        transition_count = len([row for row in transition_profiles if row.timeframe == timeframe])
        price_count = len([row for row in price_profiles if row.timeframe == timeframe])
        sequence_count = len([row for row in sequence_profiles if row.timeframe == timeframe])
        structure_cv = cv(structures)
        forward_cv = cv(forward_ranges)
        low_sample_rate = ratio(mean(low_research) + mean(low_price), max(state_count + transition_count + price_count, 1))
        sample_quality = "HIGH_PRESSURE" if low_sample_rate >= config.high_low_sample_rate else "MODERATE"
        scenario_sensitivity = sensitivity_flag(forward_cv, config.high_regime_sensitivity_threshold)
        structural_maturity = (
            "MATURE_RESEARCH_CONTEXT"
            if any(row.status in COMPLETED_STATUSES for row in rows)
            and structure_cv <= config.high_scenario_cv_threshold
            and state_count > 0
            else "REQUIRES_REVIEW"
        )
        summaries.append(
            TimeframeResearchSummary(
                timeframe=timeframe,
                scenario_count=len(rows),
                completed_scenario_count=sum(1 for row in rows if row.status in COMPLETED_STATUSES),
                total_ohlc_rows=sum(row.ohlc_rows for row in rows),
                average_structures_detected=mean(structures),
                structure_count_cv=structure_cv,
                average_states_generated=mean([row.states_generated for row in rows]),
                average_unique_states=mean([row.unique_states for row in rows]),
                most_common_state_mode=mode([row.most_common_state for row in rows]),
                average_forward_range_pips=mean(forward_ranges),
                forward_range_cv=forward_cv,
                average_direction_alignment_rate=mean([row.direction_alignment_rate for row in rows]),
                average_low_sample_conditions_research=mean(low_research),
                average_low_sample_conditions_price_outcome=mean(low_price),
                state_profile_count=state_count,
                transition_profile_count=transition_count,
                price_outcome_profile_count=price_count,
                sequence_profile_count=sequence_count,
                structural_maturity_flag=structural_maturity,
                research_sample_quality_flag=sample_quality,
                scenario_sensitivity_flag=scenario_sensitivity,
                timeframe_research_diagnostic=_diagnostic(
                    timeframe,
                    structure_cv,
                    sample_quality,
                    scenario_sensitivity,
                    state_count,
                    price_count,
                    config,
                ),
                recommended_follow_up=_follow_up(timeframe, sample_quality, scenario_sensitivity),
            )
        )
    return summaries


def build_h4_d1_findings(summaries: list[TimeframeResearchSummary]) -> list[H4D1ResearchFinding]:
    findings: list[H4D1ResearchFinding] = []
    for summary in summaries:
        findings.append(
            H4D1ResearchFinding(
                timeframe=summary.timeframe,
                finding_type="STRUCTURAL_MATURITY",
                flag=summary.structural_maturity_flag,
                message=summary.timeframe_research_diagnostic,
            )
        )
        findings.append(
            H4D1ResearchFinding(
                timeframe=summary.timeframe,
                finding_type="SAMPLE_QUALITY",
                flag=summary.research_sample_quality_flag,
                message=(
                    f"{summary.timeframe} average low sample counts are "
                    f"research={summary.average_low_sample_conditions_research:.4f}, "
                    f"price_outcome={summary.average_low_sample_conditions_price_outcome:.4f}."
                ),
            )
        )
        findings.append(
            H4D1ResearchFinding(
                timeframe=summary.timeframe,
                finding_type="SCENARIO_SENSITIVITY",
                flag=summary.scenario_sensitivity_flag,
                message=f"{summary.timeframe} forward range CV is {summary.forward_range_cv:.4f}.",
            )
        )
    return findings


def _diagnostic(
    timeframe: str,
    structure_cv: float,
    sample_quality: str,
    scenario_sensitivity: str,
    state_profile_count: int,
    price_profile_count: int,
    config: H4D1StructuralResearchConfig,
) -> str:
    if timeframe == "H4":
        if (
            structure_cv <= config.high_scenario_cv_threshold
            and sample_quality == "MODERATE"
            and scenario_sensitivity == "MODERATE"
            and state_profile_count > 0
        ):
            return "H4 structural research baseline appears mature"
        if scenario_sensitivity == "HIGH":
            return "H4 outcomes show scenario sensitivity requiring further review"
        if sample_quality == "HIGH_PRESSURE":
            return "H4 research outputs require sample adequacy review"
    if timeframe == "D1":
        if scenario_sensitivity == "HIGH" or price_profile_count > 0:
            return "D1 structural context appears regime-sensitive"
        if state_profile_count > 0 and structure_cv <= config.high_scenario_cv_threshold:
            return "D1 state distribution is structurally consistent across historical periods"
        if price_profile_count > 0:
            return "D1 price outcomes require regime-normalized interpretation"
    return "Timeframe requires further structural research review"


def _follow_up(timeframe: str, sample_quality: str, scenario_sensitivity: str) -> str:
    if timeframe == "D1" and scenario_sensitivity == "HIGH":
        return "Review D1 regime-normalized price outcome research."
    if timeframe == "H4" and sample_quality == "MODERATE":
        return "Review H4 state and transition outcome detail."
    if sample_quality == "HIGH_PRESSURE":
        return f"Review {timeframe} sample adequacy before later aggregation."
    return f"Continue {timeframe} descriptive structural research review."
