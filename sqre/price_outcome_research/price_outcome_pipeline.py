"""SQRE Price Outcome Research pipeline."""

from __future__ import annotations

from pathlib import Path
from statistics import median
from typing import Iterable

import pandas as pd

from sqre.price_outcome_research.conditions import generate_price_outcome_conditions
from sqre.price_outcome_research.config import PriceOutcomeResearchConfig
from sqre.price_outcome_research.distributions import build_price_outcome_distributions
from sqre.price_outcome_research.loader import (
    load_ohlc,
    load_price_outcome_states,
    load_price_outcome_transitions,
)
from sqre.price_outcome_research.models import (
    ConditionPriceOutcomeSummaryRow,
    PriceOutcomeDistributionRow,
    PriceOutcomeResearchSummary,
    PriceOutcomeRow,
    PriceOutcomeState,
    PriceOutcomeTransition,
)
from sqre.price_outcome_research.outcomes import build_price_outcomes
from sqre.price_outcome_research.reports import write_price_outcome_research_report
from sqre.price_outcome_research.summaries import build_condition_price_outcome_summaries


def run_price_outcome_research(
    states_path: Path | str,
    transitions_path: Path | str,
    ohlc_path: Path | str,
    output_dir: Path | str,
    report_path: Path | str,
    config: PriceOutcomeResearchConfig | None = None,
) -> PriceOutcomeResearchSummary:
    active_config = config or PriceOutcomeResearchConfig()
    output_directory = Path(output_dir)
    report = Path(report_path)
    output_directory.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    states = load_price_outcome_states(states_path)
    transitions = load_price_outcome_transitions(transitions_path)
    candles = load_ohlc(ohlc_path)
    conditions = generate_price_outcome_conditions(states, transitions)
    outcome_rows = build_price_outcomes(states, transitions, candles, conditions, active_config)
    summary_rows = build_condition_price_outcome_summaries(outcome_rows, active_config)
    distribution_rows = build_price_outcome_distributions(outcome_rows, active_config)

    price_outcomes_path = output_directory / "price_outcomes.csv"
    condition_summary_path = output_directory / "condition_price_outcome_summary.csv"
    distributions_path = output_directory / "price_outcome_distributions.csv"

    _price_outcomes_frame(outcome_rows).to_csv(price_outcomes_path, index=False)
    _summary_frame(summary_rows).to_csv(condition_summary_path, index=False)
    _distribution_frame(distribution_rows).to_csv(distributions_path, index=False)

    summary = _build_summary(
        states=states,
        transitions=transitions,
        condition_types=sorted({condition.condition_type for condition in conditions}),
        conditions_evaluated=len(conditions),
        outcome_rows=outcome_rows,
        summary_rows=summary_rows,
        distribution_rows=distribution_rows,
        config=active_config,
        price_outcomes_path=price_outcomes_path,
        condition_summary_path=condition_summary_path,
        distributions_path=distributions_path,
        report_path=report,
    )
    write_price_outcome_research_report(report, summary, outcome_rows, summary_rows, distribution_rows)
    return summary


def _price_outcomes_frame(rows: list[PriceOutcomeRow]) -> pd.DataFrame:
    columns = [
        "Outcome_ID",
        "Condition_ID",
        "Condition_Type",
        "Condition_Value",
        "Occurrence_ID",
        "Symbol",
        "Timeframe",
        "Occurrence_Start_Time",
        "Occurrence_End_Time",
        "Reference_Time",
        "Reference_Candle_Time",
        "Reference_Close",
        "Forward_Window_Candles",
        "Forward_End_Time",
        "Future_Close",
        "Max_Future_High",
        "Min_Future_Low",
        "Direction",
        "Forward_Close_Return",
        "Forward_Close_Return_Pips",
        "Forward_Close_Return_Percent",
        "Max_Favorable_Displacement_Pips",
        "Max_Adverse_Displacement_Pips",
        "Forward_Range_Pips",
        "Direction_Aligned",
        "Positive_Close_Return",
        "Negative_Close_Return",
        "Flat_Close_Return",
        "Outcome_Magnitude_Pips",
        "Complete_Forward_Window",
    ]
    return pd.DataFrame(
        [
            {
                "Outcome_ID": row.outcome_id,
                "Condition_ID": row.condition_id,
                "Condition_Type": row.condition_type,
                "Condition_Value": row.condition_value,
                "Occurrence_ID": row.occurrence_id,
                "Symbol": row.symbol,
                "Timeframe": row.timeframe,
                "Occurrence_Start_Time": row.occurrence_start_time,
                "Occurrence_End_Time": row.occurrence_end_time,
                "Reference_Time": row.reference_time,
                "Reference_Candle_Time": row.reference_candle_time,
                "Reference_Close": row.reference_close,
                "Forward_Window_Candles": row.forward_window_candles,
                "Forward_End_Time": row.forward_end_time,
                "Future_Close": row.future_close,
                "Max_Future_High": row.max_future_high,
                "Min_Future_Low": row.min_future_low,
                "Direction": row.direction,
                "Forward_Close_Return": row.forward_close_return,
                "Forward_Close_Return_Pips": row.forward_close_return_pips,
                "Forward_Close_Return_Percent": row.forward_close_return_percent,
                "Max_Favorable_Displacement_Pips": row.max_favorable_displacement_pips,
                "Max_Adverse_Displacement_Pips": row.max_adverse_displacement_pips,
                "Forward_Range_Pips": row.forward_range_pips,
                "Direction_Aligned": row.direction_aligned,
                "Positive_Close_Return": row.positive_close_return,
                "Negative_Close_Return": row.negative_close_return,
                "Flat_Close_Return": row.flat_close_return,
                "Outcome_Magnitude_Pips": row.outcome_magnitude_pips,
                "Complete_Forward_Window": row.complete_forward_window,
            }
            for row in rows
        ],
        columns=columns,
    )


def _summary_frame(rows: list[ConditionPriceOutcomeSummaryRow]) -> pd.DataFrame:
    columns = [
        "Condition_ID",
        "Condition_Type",
        "Condition_Value",
        "Forward_Window_Candles",
        "Sample_Size",
        "Incomplete_Forward_Cases",
        "Low_Sample_Size",
        "Average_Forward_Close_Return_Pips",
        "Median_Forward_Close_Return_Pips",
        "Average_Forward_Range_Pips",
        "Average_Max_Favorable_Displacement_Pips",
        "Average_Max_Adverse_Displacement_Pips",
        "Average_Outcome_Magnitude_Pips",
        "Direction_Alignment_Rate",
        "Positive_Close_Return_Rate",
        "Negative_Close_Return_Rate",
        "Flat_Close_Return_Rate",
    ]
    return pd.DataFrame(
        [
            {
                "Condition_ID": row.condition_id,
                "Condition_Type": row.condition_type,
                "Condition_Value": row.condition_value,
                "Forward_Window_Candles": row.forward_window_candles,
                "Sample_Size": row.sample_size,
                "Incomplete_Forward_Cases": row.incomplete_forward_cases,
                "Low_Sample_Size": row.low_sample_size,
                "Average_Forward_Close_Return_Pips": row.average_forward_close_return_pips,
                "Median_Forward_Close_Return_Pips": row.median_forward_close_return_pips,
                "Average_Forward_Range_Pips": row.average_forward_range_pips,
                "Average_Max_Favorable_Displacement_Pips": row.average_max_favorable_displacement_pips,
                "Average_Max_Adverse_Displacement_Pips": row.average_max_adverse_displacement_pips,
                "Average_Outcome_Magnitude_Pips": row.average_outcome_magnitude_pips,
                "Direction_Alignment_Rate": row.direction_alignment_rate,
                "Positive_Close_Return_Rate": row.positive_close_return_rate,
                "Negative_Close_Return_Rate": row.negative_close_return_rate,
                "Flat_Close_Return_Rate": row.flat_close_return_rate,
            }
            for row in rows
        ],
        columns=columns,
    )


def _distribution_frame(rows: list[PriceOutcomeDistributionRow]) -> pd.DataFrame:
    columns = [
        "Condition_ID",
        "Condition_Type",
        "Condition_Value",
        "Forward_Window_Candles",
        "Return_Bucket",
        "Count",
        "Frequency",
        "Percentage",
        "Sample_Size",
        "Low_Sample_Size",
    ]
    return pd.DataFrame(
        [
            {
                "Condition_ID": row.condition_id,
                "Condition_Type": row.condition_type,
                "Condition_Value": row.condition_value,
                "Forward_Window_Candles": row.forward_window_candles,
                "Return_Bucket": row.return_bucket,
                "Count": row.count,
                "Frequency": row.frequency,
                "Percentage": row.percentage,
                "Sample_Size": row.sample_size,
                "Low_Sample_Size": row.low_sample_size,
            }
            for row in rows
        ],
        columns=columns,
    )


def _build_summary(
    *,
    states: list[PriceOutcomeState],
    transitions: list[PriceOutcomeTransition],
    condition_types: list[str],
    conditions_evaluated: int,
    outcome_rows: list[PriceOutcomeRow],
    summary_rows: list[ConditionPriceOutcomeSummaryRow],
    distribution_rows: list[PriceOutcomeDistributionRow],
    config: PriceOutcomeResearchConfig,
    price_outcomes_path: Path,
    condition_summary_path: Path,
    distributions_path: Path,
    report_path: Path,
) -> PriceOutcomeResearchSummary:
    complete_outcomes = [row for row in outcome_rows if row.complete_forward_window]
    return PriceOutcomeResearchSummary(
        symbol=_summary_value([state.symbol for state in states]),
        timeframe=_summary_value([state.timeframe for state in states]),
        period_start=min((state.start_time for state in states), default=None),
        period_end=max((state.end_time for state in states), default=None),
        conditions_evaluated=conditions_evaluated,
        condition_types=condition_types,
        price_outcomes_generated=len(outcome_rows),
        forward_windows=list(config.forward_candles),
        pip_size=config.pip_size,
        minimum_sample_size=config.minimum_sample_size,
        summary_rows=len(summary_rows),
        distribution_rows=len(distribution_rows),
        low_sample_conditions=sum(row.low_sample_size for row in summary_rows),
        average_forward_close_return_pips=_average(
            row.forward_close_return_pips for row in complete_outcomes
        ),
        median_forward_close_return_pips=_median(
            row.forward_close_return_pips for row in complete_outcomes
        ),
        average_forward_range_pips=_average(row.forward_range_pips for row in complete_outcomes),
        average_favorable_displacement_pips=_average(
            row.max_favorable_displacement_pips for row in complete_outcomes
        ),
        average_adverse_displacement_pips=_average(
            row.max_adverse_displacement_pips for row in complete_outcomes
        ),
        average_outcome_magnitude_pips=_average(
            row.outcome_magnitude_pips for row in complete_outcomes
        ),
        direction_alignment_rate=_rate(
            sum(row.direction_aligned for row in complete_outcomes),
            len(complete_outcomes),
        ),
        most_observed_condition=_most_observed_condition(summary_rows),
        largest_average_forward_range_condition=_best_condition(
            summary_rows,
            "average_forward_range_pips",
        ),
        highest_direction_alignment_condition=_best_condition(
            summary_rows,
            "direction_alignment_rate",
        ),
        price_outcomes_path=price_outcomes_path,
        condition_price_outcome_summary_path=condition_summary_path,
        price_outcome_distributions_path=distributions_path,
        report_path=report_path,
    )


def _summary_value(values: list[str]) -> str:
    unique_values = sorted(set(values))
    if not unique_values:
        return "UNKNOWN"
    if len(unique_values) == 1:
        return unique_values[0]
    return "MULTIPLE"


def _average(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


def _median(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return float(median(items))


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return count / total


def _most_observed_condition(rows: list[ConditionPriceOutcomeSummaryRow]) -> str:
    if not rows:
        return "NONE"
    best = max(rows, key=lambda row: (row.sample_size, row.condition_value))
    return best.condition_value


def _best_condition(rows: list[ConditionPriceOutcomeSummaryRow], attr: str) -> str:
    if not rows:
        return "NONE"
    best = max(rows, key=lambda row: (getattr(row, attr), row.sample_size, row.condition_value))
    return best.condition_value
