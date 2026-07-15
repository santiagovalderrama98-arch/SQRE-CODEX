"""Price outcome H4/D1 structural research profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.consistency import adequacy_flag, cv, mean, sensitivity_flag
from sqre.h4_d1_structural_research.loader import read_csv, resolve_column
from sqre.h4_d1_structural_research.models import PriceOutcomeProfile, ScenarioData


def build_price_outcome_profiles(
    scenarios: list[ScenarioData],
    config: H4D1StructuralResearchConfig,
) -> list[PriceOutcomeProfile]:
    grouped: dict[tuple[str, str, str, int], list[tuple[str, dict[str, float]]]] = defaultdict(list)

    for scenario in scenarios:
        inventory = scenario.inventory
        frame = read_csv(scenario.price_outcome_summary_path)
        if frame.empty:
            continue
        columns = _columns(frame)
        condition_type = columns.get("condition_type")
        condition_label = columns.get("condition_value") or columns.get("condition_label")
        forward_window = columns.get("forward_window_candles") or columns.get("forward_window")
        if condition_type is None or condition_label is None or forward_window is None:
            continue
        for _, row in frame.iterrows():
            key = (
                inventory.timeframe,
                str(row[condition_type]),
                str(row[condition_label]),
                int(_number(row, forward_window)),
            )
            grouped[key].append((inventory.scenario_id, _metrics(row, columns)))

    profiles: list[PriceOutcomeProfile] = []
    for key, items in sorted(grouped.items()):
        timeframe, condition_type, condition_label, forward_window = key
        scenario_ids = sorted({scenario_id for scenario_id, _ in items})
        sample_sizes = [metrics["sample_size"] for _, metrics in items]
        forward_ranges = [metrics["average_forward_range_pips"] for _, metrics in items]
        magnitudes = [metrics["average_outcome_magnitude_pips"] for _, metrics in items]
        total_sample = int(sum(sample_sizes))
        forward_cv = cv(forward_ranges)
        magnitude_cv = cv(magnitudes)
        sample_flag = adequacy_flag(total_sample, config.minimum_sample_size)
        sensitivity = sensitivity_flag(max(forward_cv, magnitude_cv), config.high_regime_sensitivity_threshold)
        profiles.append(
            PriceOutcomeProfile(
                timeframe=timeframe,
                condition_type=condition_type,
                condition_label=condition_label,
                forward_window=forward_window,
                scenario_count=len(scenario_ids),
                scenarios_present=";".join(scenario_ids),
                total_sample_size=total_sample,
                average_sample_size_per_scenario=mean(sample_sizes),
                average_forward_close_return_pips=mean([metrics["average_forward_close_return_pips"] for _, metrics in items]),
                median_forward_close_return_pips=mean([metrics["median_forward_close_return_pips"] for _, metrics in items]),
                average_forward_range_pips=mean(forward_ranges),
                average_favorable_displacement_pips=mean(
                    [metrics["average_favorable_displacement_pips"] for _, metrics in items]
                ),
                average_adverse_displacement_pips=mean(
                    [metrics["average_adverse_displacement_pips"] for _, metrics in items]
                ),
                average_outcome_magnitude_pips=mean(magnitudes),
                average_direction_alignment_rate=mean([metrics["direction_alignment_rate"] for _, metrics in items]),
                forward_range_cv=forward_cv,
                outcome_magnitude_cv=magnitude_cv,
                scenario_sensitivity_flag=sensitivity,
                sample_adequacy_flag=sample_flag,
                outcome_profile_diagnostic=_diagnostic(condition_label, sample_flag, sensitivity),
            )
        )
    return profiles


def _columns(frame) -> dict[str, str]:
    keys = [
        "Condition_Type",
        "Condition_Value",
        "Condition_Label",
        "Forward_Window_Candles",
        "Forward_Window",
        "Sample_Size",
        "Average_Forward_Close_Return_Pips",
        "Median_Forward_Close_Return_Pips",
        "Average_Forward_Range_Pips",
        "Average_Max_Favorable_Displacement_Pips",
        "Average_Favorable_Displacement_Pips",
        "Average_Max_Adverse_Displacement_Pips",
        "Average_Adverse_Displacement_Pips",
        "Average_Outcome_Magnitude_Pips",
        "Direction_Alignment_Rate",
    ]
    return {key.lower(): actual for key in keys if (actual := resolve_column(frame, key)) is not None}


def _metrics(row, columns: dict[str, str]) -> dict[str, float]:
    return {
        "sample_size": _number(row, columns.get("sample_size")),
        "average_forward_close_return_pips": _number(row, columns.get("average_forward_close_return_pips")),
        "median_forward_close_return_pips": _number(row, columns.get("median_forward_close_return_pips")),
        "average_forward_range_pips": _number(row, columns.get("average_forward_range_pips")),
        "average_favorable_displacement_pips": _number(
            row,
            columns.get("average_max_favorable_displacement_pips")
            or columns.get("average_favorable_displacement_pips"),
        ),
        "average_adverse_displacement_pips": _number(
            row,
            columns.get("average_max_adverse_displacement_pips") or columns.get("average_adverse_displacement_pips"),
        ),
        "average_outcome_magnitude_pips": _number(row, columns.get("average_outcome_magnitude_pips")),
        "direction_alignment_rate": _number(row, columns.get("direction_alignment_rate")),
    }


def _number(row, column: str | None) -> float:
    if column is None:
        return 0.0
    try:
        return float(row[column])
    except (TypeError, ValueError):
        return 0.0


def _diagnostic(condition_label: str, sample_flag: str, sensitivity: str) -> str:
    if sample_flag == "LOW_SAMPLE":
        return f"{condition_label} outcome profile requires sample adequacy review"
    if sensitivity == "HIGH":
        return f"{condition_label} outcome profile shows scenario sensitivity"
    return f"{condition_label} outcome profile is available for descriptive review"
