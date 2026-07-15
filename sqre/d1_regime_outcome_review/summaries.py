"""Summaries for D1 regime outcome review."""

from __future__ import annotations

from collections import Counter, defaultdict

from sqre.d1_regime_outcome_review.config import D1RegimeOutcomeReviewConfig
from sqre.d1_regime_outcome_review.dispersion import mean
from sqre.d1_regime_outcome_review.findings import d1_review_diagnostic
from sqre.d1_regime_outcome_review.models import (
    ConditionLabelSummary,
    ConditionQualityInventoryRow,
    D1OutcomeReviewSummary,
    DispersionSummary,
    SampleAdequacySummary,
)
from sqre.d1_regime_outcome_review.sample_adequacy import ratio


def build_condition_label_summaries(
    rows: list[ConditionQualityInventoryRow],
    condition_kind: str,
) -> list[ConditionLabelSummary]:
    grouped: dict[str, list[ConditionQualityInventoryRow]] = defaultdict(list)
    for row in rows:
        if condition_kind.upper() in row.condition_type.upper():
            grouped[row.condition_label].append(row)
    summaries: list[ConditionLabelSummary] = []
    for label, items in sorted(grouped.items()):
        base = _label_summary(label, items)
        diagnostic = _condition_diagnostic(condition_kind, base)
        summaries.append(
            ConditionLabelSummary(
                condition_label=base.condition_label,
                profile_count=base.profile_count,
                research_ready_profile_count=base.research_ready_profile_count,
                regime_sensitive_profile_count=base.regime_sensitive_profile_count,
                low_sample_profile_count=base.low_sample_profile_count,
                limited_coverage_profile_count=base.limited_coverage_profile_count,
                average_total_sample_size=base.average_total_sample_size,
                average_regime_count=base.average_regime_count,
                average_forward_range_cv=base.average_forward_range_cv,
                average_outcome_magnitude_cv=base.average_outcome_magnitude_cv,
                dominant_condition_research_class=base.dominant_condition_research_class,
                state_condition_diagnostic=diagnostic if condition_kind == "STATE" else "",
                transition_condition_diagnostic=diagnostic if condition_kind == "TRANSITION" else "",
                recommended_follow_up=_condition_follow_up(base),
            )
        )
    return summaries


def build_dispersion_summaries(rows: list[ConditionQualityInventoryRow]) -> list[DispersionSummary]:
    grouped: dict[str, list[ConditionQualityInventoryRow]] = defaultdict(list)
    for row in rows:
        grouped[row.condition_type].append(row)
    return [_dispersion_summary(condition_type, items) for condition_type, items in sorted(grouped.items())]


def build_sample_adequacy_summaries(rows: list[ConditionQualityInventoryRow]) -> list[SampleAdequacySummary]:
    grouped: dict[str, list[ConditionQualityInventoryRow]] = {"TOTAL": rows}
    for row in rows:
        grouped.setdefault(row.condition_type, []).append(row)
    return [_sample_summary(scope, items) for scope, items in grouped.items()]


def build_d1_review_summary(
    rows: list[ConditionQualityInventoryRow],
    config: D1RegimeOutcomeReviewConfig,
) -> D1OutcomeReviewSummary:
    state_rows = [row for row in rows if "STATE" in row.condition_type.upper()]
    transition_rows = [row for row in rows if "TRANSITION" in row.condition_type.upper()]
    research_ready = [row for row in rows if row.condition_research_class == "RESEARCH_READY_DESCRIPTIVE"]
    regime_sensitive = [row for row in rows if row.sensitivity_class == "HIGH" or row.dispersion_class == "HIGH"]
    low_sample = [row for row in rows if row.sample_adequacy_class == "LOW_SAMPLE"]
    limited = [row for row in rows if row.regime_coverage_class == "LIMITED"]
    high_dispersion = [row for row in rows if row.dispersion_class == "HIGH"]
    diagnostic = d1_review_diagnostic(len(rows), len(research_ready), len(regime_sensitive), len(low_sample), config)
    return D1OutcomeReviewSummary(
        timeframe="D1",
        input_profile_count=len(rows),
        research_ready_profile_count=len(research_ready),
        regime_sensitive_profile_count=len(regime_sensitive),
        low_sample_profile_count=len(low_sample),
        limited_coverage_profile_count=len(limited),
        high_dispersion_profile_count=len(high_dispersion),
        state_profile_count=len(state_rows),
        transition_profile_count=len(transition_rows),
        research_ready_state_profile_count=sum(
            1 for row in state_rows if row.condition_research_class == "RESEARCH_READY_DESCRIPTIVE"
        ),
        research_ready_transition_profile_count=sum(
            1 for row in transition_rows if row.condition_research_class == "RESEARCH_READY_DESCRIPTIVE"
        ),
        average_forward_range_cv=mean([row.forward_range_cv for row in rows]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in rows]),
        average_direction_alignment_rate=mean([row.average_direction_alignment_rate for row in rows]),
        sample_adequacy_profile=_sample_profile(len(rows), len(low_sample), config),
        outcome_dispersion_profile="HIGH_DISPERSION" if high_dispersion else "MIXED_DISPERSION",
        regime_sensitivity_profile="REGIME_SENSITIVE" if regime_sensitive else "MIXED",
        d1_outcome_review_diagnostic=diagnostic,
        recommended_follow_up=_summary_follow_up(diagnostic),
    )


def _label_summary(label: str, items: list[ConditionQualityInventoryRow]) -> ConditionLabelSummary:
    return ConditionLabelSummary(
        condition_label=label,
        profile_count=len(items),
        research_ready_profile_count=sum(1 for row in items if row.condition_research_class == "RESEARCH_READY_DESCRIPTIVE"),
        regime_sensitive_profile_count=sum(1 for row in items if row.sensitivity_class == "HIGH" or row.dispersion_class == "HIGH"),
        low_sample_profile_count=sum(1 for row in items if row.sample_adequacy_class == "LOW_SAMPLE"),
        limited_coverage_profile_count=sum(1 for row in items if row.regime_coverage_class == "LIMITED"),
        average_total_sample_size=mean([row.total_sample_size for row in items]),
        average_regime_count=mean([row.regime_count for row in items]),
        average_forward_range_cv=mean([row.forward_range_cv for row in items]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in items]),
        dominant_condition_research_class=_mode([row.condition_research_class for row in items]),
    )


def _dispersion_summary(condition_type: str, items: list[ConditionQualityInventoryRow]) -> DispersionSummary:
    high = sum(1 for row in items if row.dispersion_class == "HIGH")
    return DispersionSummary(
        condition_type=condition_type,
        profile_count=len(items),
        average_forward_range_cv=mean([row.forward_range_cv for row in items]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in items]),
        low_dispersion_profile_count=sum(1 for row in items if row.dispersion_class == "LOW"),
        moderate_dispersion_profile_count=sum(1 for row in items if row.dispersion_class == "MODERATE"),
        high_dispersion_profile_count=high,
        stable_sensitivity_profile_count=sum(1 for row in items if row.sensitivity_class == "STABLE"),
        moderate_sensitivity_profile_count=sum(1 for row in items if row.sensitivity_class == "MODERATE"),
        high_sensitivity_profile_count=sum(1 for row in items if row.sensitivity_class == "HIGH"),
        outcome_dispersion_diagnostic=(
            "Condition type contains high dispersion profiles" if high else "Condition type dispersion is mixed or moderate"
        ),
    )


def _sample_summary(scope: str, items: list[ConditionQualityInventoryRow]) -> SampleAdequacySummary:
    total = len(items)
    adequate = sum(1 for row in items if row.sample_adequacy_class == "ADEQUATE")
    low_sample = sum(1 for row in items if row.sample_adequacy_class == "LOW_SAMPLE")
    limited = sum(1 for row in items if row.regime_coverage_class == "LIMITED")
    ready = sum(1 for row in items if row.condition_research_class == "RESEARCH_READY_DESCRIPTIVE")
    sensitive = sum(1 for row in items if row.sensitivity_class == "HIGH" or row.dispersion_class == "HIGH")
    return SampleAdequacySummary(
        scope=scope,
        profile_count=total,
        adequate_profile_count=adequate,
        low_sample_profile_count=low_sample,
        limited_coverage_profile_count=limited,
        research_ready_profile_count=ready,
        regime_sensitive_profile_count=sensitive,
        adequate_profile_ratio=ratio(adequate, total),
        low_sample_profile_ratio=ratio(low_sample, total),
        limited_coverage_profile_ratio=ratio(limited, total),
        research_ready_profile_ratio=ratio(ready, total),
        sample_adequacy_diagnostic=(
            "Sample adequacy requires review" if low_sample > adequate else "Sample adequacy profile supports review"
        ),
    )


def _condition_diagnostic(condition_kind: str, summary: ConditionLabelSummary) -> str:
    if summary.low_sample_profile_count:
        return f"{condition_kind.title()} condition requires sample adequacy review"
    if summary.limited_coverage_profile_count:
        return f"{condition_kind.title()} condition has limited regime coverage"
    if summary.regime_sensitive_profile_count:
        return f"{condition_kind.title()} condition requires regime-sensitive interpretation"
    return f"{condition_kind.title()} condition suitable for deeper descriptive review"


def _condition_follow_up(summary: ConditionLabelSummary) -> str:
    if summary.low_sample_profile_count:
        return "Review sample adequacy for this condition label."
    if summary.limited_coverage_profile_count:
        return "Review regime coverage for this condition label."
    if summary.regime_sensitive_profile_count:
        return "Review regime-sensitive behavior for this condition label."
    return "Continue deeper descriptive condition review."


def _sample_profile(total: int, low_sample_count: int, config: D1RegimeOutcomeReviewConfig) -> str:
    if ratio(low_sample_count, total) >= config.low_sample_share_threshold:
        return "SAMPLE_CONSTRAINED"
    return "MIXED_SAMPLE_ADEQUACY"


def _summary_follow_up(diagnostic: str) -> str:
    if "sample constrained" in diagnostic:
        return "Review sample adequacy before broader condition aggregation."
    if "regime-sensitive" in diagnostic:
        return "Review regime-sensitive profiles before broader aggregation."
    return "Continue deeper descriptive review for the usable condition subset."


def _mode(values: list[str]) -> str:
    clean = [value for value in values if value]
    return Counter(clean).most_common(1)[0][0] if clean else ""
