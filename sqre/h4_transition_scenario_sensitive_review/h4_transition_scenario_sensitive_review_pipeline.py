"""Pipeline for H4 transition scenario-sensitive profile review."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_transition_scenario_sensitive_review.config import H4TransitionScenarioSensitiveReviewConfig
from sqre.h4_transition_scenario_sensitive_review.deviation_drivers import (
    primary_deviating_metric,
    primary_scenario_deviation_metric,
    scenario_deviation_intensity_class,
)
from sqre.h4_transition_scenario_sensitive_review.findings import (
    profile_diagnostic,
    profile_follow_up,
    scenario_deviation_diagnostic,
    summary_diagnostic,
    summary_follow_up,
)
from sqre.h4_transition_scenario_sensitive_review.loader import (
    load_scenario_breakdown,
    load_scenario_comparisons,
    load_scenario_sensitive_profiles,
    optional_file_status,
)
from sqre.h4_transition_scenario_sensitive_review.models import (
    H4TransitionScenarioSensitiveReviewResult,
    H4TransitionScenarioSensitiveReviewSummary,
    ProfileReviewRow,
    ScenarioComparisonInput,
    ScenarioDeviationDetailRow,
    ScenarioSensitiveTransitionProfileInput,
)
from sqre.h4_transition_scenario_sensitive_review.near_candidate_review import (
    build_focus_profile_review,
    build_near_aggregation_candidates,
)
from sqre.h4_transition_scenario_sensitive_review.profile_selector import (
    dominant_sensitivity,
    focus_transition_flag,
    h4_review_readiness_flag,
    most_common,
    near_aggregation_candidate_flag,
    select_review_profiles,
    transition_sensitivity_class,
)
from sqre.h4_transition_scenario_sensitive_review.reports import write_review_outputs
from sqre.h4_transition_scenario_sensitive_review.scenario_patterns import build_scenario_recurrent_deviation_summary
from sqre.h4_transition_scenario_sensitive_review.transition_family_review import (
    build_transition_family_sensitivity_summary,
    mean,
)
from sqre.h4_transition_scenario_sensitive_review.transition_state_review import (
    build_source_state_sensitivity_summary,
    build_target_state_sensitivity_summary,
)
from sqre.h4_transition_scenario_sensitive_review.transition_window_review import (
    build_forward_window_sensitivity_summary,
)


def run_h4_transition_scenario_sensitive_review(
    dispersion_review_dir: Path | str,
    transition_deep_dive_dir: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: H4TransitionScenarioSensitiveReviewConfig | None = None,
) -> H4TransitionScenarioSensitiveReviewResult:
    active_config = config or H4TransitionScenarioSensitiveReviewConfig()
    resolved_dispersion_dir = Path(dispersion_review_dir)
    resolved_deep_dive_dir = Path(transition_deep_dive_dir)
    resolved_output_dir = Path(output_dir)
    resolved_report_path = Path(report_path)

    profiles = load_scenario_sensitive_profiles(resolved_dispersion_dir)
    comparisons = load_scenario_comparisons(resolved_deep_dive_dir)
    breakdown = load_scenario_breakdown(resolved_deep_dive_dir)

    selected_profiles = select_review_profiles(profiles, active_config)
    profile_reviews = build_profile_reviews(selected_profiles, active_config)
    scenario_details = build_scenario_deviation_details(selected_profiles, comparisons, active_config)
    scenario_summaries = build_scenario_recurrent_deviation_summary(scenario_details)
    family_summaries = build_transition_family_sensitivity_summary(profile_reviews)
    source_state_summaries = build_source_state_sensitivity_summary(profile_reviews)
    target_state_summaries = build_target_state_sensitivity_summary(profile_reviews)
    window_summaries = build_forward_window_sensitivity_summary(profile_reviews)
    near_candidates = build_near_aggregation_candidates(profile_reviews)
    focus_profiles = build_focus_profile_review(profile_reviews)
    summary = _build_summary(
        profile_reviews,
        focus_profiles,
        scenario_summaries,
        len(profiles),
        len(near_candidates),
    )
    missing_optional_files = [
        name for name, present in optional_file_status(resolved_dispersion_dir, resolved_deep_dive_dir).items() if not present
    ]

    result = H4TransitionScenarioSensitiveReviewResult(
        dispersion_review_dir=resolved_dispersion_dir,
        transition_deep_dive_dir=resolved_deep_dive_dir,
        output_dir=resolved_output_dir,
        report_path=resolved_report_path,
        scenario_sensitive_profiles_loaded=len(profiles),
        comparison_rows_loaded=len(comparisons),
        breakdown_rows_loaded=len(breakdown),
        reviewed_profiles=profile_reviews,
        focus_profiles=focus_profiles,
        scenario_details=scenario_details,
        scenario_summaries=scenario_summaries,
        family_summaries=family_summaries,
        source_state_summaries=source_state_summaries,
        target_state_summaries=target_state_summaries,
        window_summaries=window_summaries,
        near_candidates=near_candidates,
        review_summary=summary,
        missing_optional_files=missing_optional_files,
    )
    return write_review_outputs(result)


def build_profile_reviews(
    profiles: list[ScenarioSensitiveTransitionProfileInput],
    config: H4TransitionScenarioSensitiveReviewConfig,
) -> list[ProfileReviewRow]:
    rows: list[ProfileReviewRow] = []
    for profile in profiles:
        sensitivity = transition_sensitivity_class(
            profile.high_deviation_scenario_count,
            profile.moderate_deviation_scenario_count,
            profile.dominant_deviation_class,
            profile.profile_dispersion_class,
        )
        focus_flag = focus_transition_flag(profile.condition_label, config)
        near_flag = near_aggregation_candidate_flag(
            profile.total_sample_size,
            profile.scenario_count,
            profile.high_deviation_scenario_count,
            sensitivity,
            config,
        )
        rows.append(
            ProfileReviewRow(
                condition_label=profile.condition_label,
                source_state=profile.source_state,
                target_state=profile.target_state,
                transition_family=profile.transition_family,
                forward_window=profile.forward_window,
                scenario_count=profile.scenario_count,
                total_sample_size=profile.total_sample_size,
                average_forward_range_pips=profile.average_forward_range_pips,
                average_outcome_magnitude_pips=profile.average_outcome_magnitude_pips,
                average_direction_alignment_rate=profile.average_direction_alignment_rate,
                forward_range_cv=profile.forward_range_cv,
                outcome_magnitude_cv=profile.outcome_magnitude_cv,
                direction_alignment_dispersion=profile.direction_alignment_dispersion,
                high_deviation_scenario_count=profile.high_deviation_scenario_count,
                moderate_deviation_scenario_count=profile.moderate_deviation_scenario_count,
                low_deviation_scenario_count=profile.low_deviation_scenario_count,
                dominant_deviation_class=profile.dominant_deviation_class,
                dispersion_driver_class=profile.dispersion_driver_class,
                primary_deviating_metric=primary_deviating_metric(
                    profile.forward_range_cv,
                    profile.outcome_magnitude_cv,
                    profile.direction_alignment_dispersion,
                    config,
                ),
                transition_sensitivity_class=sensitivity,
                focus_transition_flag=focus_flag,
                near_aggregation_candidate_flag=near_flag,
                profile_review_diagnostic=profile_diagnostic(sensitivity),
                recommended_follow_up=profile_follow_up(sensitivity, near_flag),
            )
        )
    return rows


def build_scenario_deviation_details(
    profiles: list[ScenarioSensitiveTransitionProfileInput],
    comparisons: list[ScenarioComparisonInput],
    config: H4TransitionScenarioSensitiveReviewConfig,
) -> list[ScenarioDeviationDetailRow]:
    selected_keys = {(profile.condition_label, profile.forward_window) for profile in profiles}
    rows: list[ScenarioDeviationDetailRow] = []
    for comparison in comparisons:
        if (comparison.condition_label, comparison.forward_window) not in selected_keys:
            continue
        intensity = scenario_deviation_intensity_class(comparison.scenario_deviation_class)
        rows.append(
            ScenarioDeviationDetailRow(
                condition_label=comparison.condition_label,
                source_state=comparison.source_state,
                target_state=comparison.target_state,
                transition_family=comparison.transition_family,
                forward_window=comparison.forward_window,
                scenario_id=comparison.scenario_id,
                sample_size=comparison.sample_size,
                forward_range_vs_profile_avg=comparison.forward_range_vs_profile_avg,
                outcome_magnitude_vs_profile_avg=comparison.outcome_magnitude_vs_profile_avg,
                direction_alignment_vs_profile_avg=comparison.direction_alignment_vs_profile_avg,
                scenario_deviation_class=comparison.scenario_deviation_class,
                primary_scenario_deviation_metric=primary_scenario_deviation_metric(comparison, config),
                scenario_deviation_intensity_class=intensity,
                scenario_deviation_diagnostic=scenario_deviation_diagnostic(intensity),
            )
        )
    return sorted(rows, key=lambda row: (row.condition_label, row.forward_window, row.scenario_id))


def _build_summary(
    profile_reviews: list[ProfileReviewRow],
    focus_profiles: list,
    scenario_summaries: list,
    scenario_sensitive_profile_count: int,
    near_candidate_count: int,
) -> H4TransitionScenarioSensitiveReviewSummary:
    high = sum(
        1 for row in profile_reviews if row.transition_sensitivity_class == "HIGH_TRANSITION_SCENARIO_SENSITIVITY"
    )
    moderate = sum(
        1 for row in profile_reviews if row.transition_sensitivity_class == "MODERATE_TRANSITION_SCENARIO_SENSITIVITY"
    )
    low = sum(
        1 for row in profile_reviews if row.transition_sensitivity_class == "LOW_TRANSITION_SCENARIO_SENSITIVITY"
    )
    high_recurrent = sum(
        1 for row in scenario_summaries if row.scenario_recurrent_deviation_class == "HIGH_RECURRENT_DEVIATION"
    )
    moderate_recurrent = sum(
        1 for row in scenario_summaries if row.scenario_recurrent_deviation_class == "MODERATE_RECURRENT_DEVIATION"
    )
    low_recurrent = sum(
        1 for row in scenario_summaries if row.scenario_recurrent_deviation_class == "LOW_RECURRENT_DEVIATION"
    )
    readiness = h4_review_readiness_flag(len(profile_reviews), near_candidate_count)
    return H4TransitionScenarioSensitiveReviewSummary(
        timeframe="H4",
        scenario_sensitive_profile_count=scenario_sensitive_profile_count,
        reviewed_profile_count=len(profile_reviews),
        focus_profile_count=len(focus_profiles),
        high_sensitivity_profile_count=high,
        moderate_sensitivity_profile_count=moderate,
        low_sensitivity_profile_count=low,
        near_aggregation_candidate_count=near_candidate_count,
        scenario_count=len(scenario_summaries),
        high_recurrent_deviation_scenario_count=high_recurrent,
        moderate_recurrent_deviation_scenario_count=moderate_recurrent,
        low_recurrent_deviation_scenario_count=low_recurrent,
        average_forward_range_cv=mean([row.forward_range_cv for row in profile_reviews]),
        average_outcome_magnitude_cv=mean([row.outcome_magnitude_cv for row in profile_reviews]),
        average_direction_alignment_dispersion=mean([row.direction_alignment_dispersion for row in profile_reviews]),
        dominant_dispersion_driver=most_common([row.dispersion_driver_class for row in profile_reviews], "LOW_DISPERSION"),
        h4_transition_scenario_sensitive_profile=dominant_sensitivity(
            [row.transition_sensitivity_class for row in profile_reviews]
        ),
        h4_review_readiness_flag=readiness,
        h4_transition_scenario_sensitive_review_diagnostic=summary_diagnostic(
            near_candidate_count,
            high,
            len(profile_reviews),
        ),
        recommended_follow_up=summary_follow_up(near_candidate_count, high, len(profile_reviews)),
    )
