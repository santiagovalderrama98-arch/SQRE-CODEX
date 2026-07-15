"""Build D1 regime-normalized outcome profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.d1_regime_normalized_research.config import D1RegimeResearchConfig
from sqre.d1_regime_normalized_research.loader import integer_value, number_value, read_csv, text_value
from sqre.d1_regime_normalized_research.models import (
    D1RegimeConditionOutcome,
    D1RegimeConditionProfile,
    D1RegimeScenarioData,
)
from sqre.d1_regime_normalized_research.regime_sensitivity import (
    cv,
    mean,
    profile_diagnostic,
    regime_coverage_flag,
    regime_sensitivity_flag,
    sample_adequacy_flag,
)


def build_condition_outcomes(
    scenarios: list[D1RegimeScenarioData],
    config: D1RegimeResearchConfig,
) -> list[D1RegimeConditionOutcome]:
    outcomes: list[D1RegimeConditionOutcome] = []
    for scenario in scenarios:
        frame = read_csv(scenario.price_outcome_summary_path)
        for _, row in frame.iterrows():
            condition_type = text_value(row, "Condition_Type")
            condition_label = _condition_label(row)
            forward_window = _forward_window(row)
            sample_size = integer_value(row, "Sample_Size")
            outcomes.append(
                D1RegimeConditionOutcome(
                    regime_id=scenario.inventory.regime_id,
                    regime_label=scenario.inventory.regime_label,
                    scenario_id=scenario.inventory.scenario_id,
                    timeframe=scenario.inventory.timeframe,
                    condition_type=condition_type,
                    condition_label=condition_label,
                    forward_window=forward_window,
                    sample_size=sample_size,
                    average_forward_close_return_pips=number_value(row, "Average_Forward_Close_Return_Pips"),
                    median_forward_close_return_pips=number_value(row, "Median_Forward_Close_Return_Pips"),
                    average_forward_range_pips=number_value(row, "Average_Forward_Range_Pips"),
                    average_favorable_displacement_pips=_first_number(
                        row,
                        ["Average_Max_Favorable_Displacement_Pips", "Average_Favorable_Displacement_Pips"],
                    ),
                    average_adverse_displacement_pips=_first_number(
                        row,
                        ["Average_Max_Adverse_Displacement_Pips", "Average_Adverse_Displacement_Pips"],
                    ),
                    average_outcome_magnitude_pips=number_value(row, "Average_Outcome_Magnitude_Pips"),
                    direction_alignment_rate=number_value(row, "Direction_Alignment_Rate"),
                    sample_adequacy_flag=sample_adequacy_flag(sample_size, config),
                )
            )
    return outcomes


def build_normalized_condition_profiles(
    outcomes: list[D1RegimeConditionOutcome],
    config: D1RegimeResearchConfig,
) -> list[D1RegimeConditionProfile]:
    grouped: dict[tuple[str, str, int], list[D1RegimeConditionOutcome]] = defaultdict(list)
    for outcome in outcomes:
        grouped[(outcome.condition_type, outcome.condition_label, outcome.forward_window)].append(outcome)

    profiles: list[D1RegimeConditionProfile] = []
    for (condition_type, condition_label, forward_window), rows in sorted(grouped.items()):
        regimes = sorted({row.regime_id for row in rows})
        scenarios = sorted({row.scenario_id for row in rows})
        total_sample_size = sum(row.sample_size for row in rows)
        forward_close = [row.average_forward_close_return_pips for row in rows]
        medians = [row.median_forward_close_return_pips for row in rows]
        ranges = [row.average_forward_range_pips for row in rows]
        magnitudes = [row.average_outcome_magnitude_pips for row in rows]
        alignments = [row.direction_alignment_rate for row in rows]
        sample_flag = sample_adequacy_flag(total_sample_size, config)
        coverage_flag = regime_coverage_flag(len(regimes), config)
        range_cv = cv(ranges)
        magnitude_cv = cv(magnitudes)
        sensitivity_flag = regime_sensitivity_flag(range_cv, magnitude_cv, config)
        profiles.append(
            D1RegimeConditionProfile(
                condition_type=condition_type,
                condition_label=condition_label,
                forward_window=forward_window,
                regime_count=len(regimes),
                regimes_present=";".join(regimes),
                scenario_count=len(scenarios),
                total_sample_size=total_sample_size,
                average_sample_size_per_regime=total_sample_size / len(regimes) if regimes else 0.0,
                average_forward_close_return_pips=mean(forward_close),
                median_forward_close_return_pips_avg=mean(medians),
                average_forward_range_pips=mean(ranges),
                average_outcome_magnitude_pips=mean(magnitudes),
                average_direction_alignment_rate=mean(alignments),
                forward_close_return_cv=cv(forward_close),
                forward_range_cv=range_cv,
                outcome_magnitude_cv=magnitude_cv,
                direction_alignment_cv=cv(alignments),
                min_forward_range_pips=min(ranges) if ranges else 0.0,
                max_forward_range_pips=max(ranges) if ranges else 0.0,
                range_dispersion_pips=(max(ranges) - min(ranges)) if ranges else 0.0,
                min_outcome_magnitude_pips=min(magnitudes) if magnitudes else 0.0,
                max_outcome_magnitude_pips=max(magnitudes) if magnitudes else 0.0,
                outcome_magnitude_dispersion_pips=(max(magnitudes) - min(magnitudes)) if magnitudes else 0.0,
                sample_adequacy_flag=sample_flag,
                regime_coverage_flag=coverage_flag,
                regime_sensitivity_flag=sensitivity_flag,
                condition_profile_diagnostic=profile_diagnostic(sample_flag, coverage_flag, sensitivity_flag),
                recommended_follow_up=_follow_up(condition_type, sample_flag, coverage_flag, sensitivity_flag),
            )
        )
    return profiles


def state_condition_profiles(profiles: list[D1RegimeConditionProfile]) -> list[D1RegimeConditionProfile]:
    return [profile for profile in profiles if "STATE" in profile.condition_type.upper()]


def transition_condition_profiles(profiles: list[D1RegimeConditionProfile]) -> list[D1RegimeConditionProfile]:
    return [profile for profile in profiles if "TRANSITION" in profile.condition_type.upper()]


def _condition_label(row) -> str:
    label = text_value(row, "Condition_Label")
    if label:
        return label
    label = text_value(row, "Condition_Value")
    if label:
        return label
    return text_value(row, "Condition_ID")


def _forward_window(row) -> int:
    value = integer_value(row, "Forward_Window")
    if value:
        return value
    value = integer_value(row, "Forward_Window_Candles")
    return value if value else integer_value(row, "Forward_Candles")


def _first_number(row, columns: list[str]) -> float:
    for column in columns:
        value = number_value(row, column, default=None)
        if value is not None:
            return value
    return 0.0


def _follow_up(condition_type: str, sample_flag: str, coverage_flag: str, sensitivity_flag: str) -> str:
    if sample_flag == "LOW_SAMPLE":
        return "Review D1 sample adequacy for this condition profile."
    if coverage_flag == "LIMITED":
        return "Review D1 regime coverage for this condition profile."
    if sensitivity_flag == "HIGH":
        return "Review D1 regime-normalized dispersion for this condition profile."
    if "TRANSITION" in condition_type.upper():
        return "Continue D1 transition outcome regime analysis."
    return "Continue D1 state outcome regime review."
