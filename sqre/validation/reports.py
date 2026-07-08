"""Report writer for SQRE multi-scenario validation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqre.validation.models import FAILED, MISSING_INPUT, SKIPPED, ScenarioMetrics, ValidationConfig, ValidationSummary


def write_validation_report(
    path: Path | str,
    *,
    config: ValidationConfig,
    summary: ValidationSummary,
    metrics: list[ScenarioMetrics],
) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(config=config, summary=summary, metrics=metrics), encoding="utf-8")
    return report_path


def _build_report(
    *,
    config: ValidationConfig,
    summary: ValidationSummary,
    metrics: list[ScenarioMetrics],
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    completed = [item for item in metrics if item.status == "COMPLETED"]
    missing = [item for item in metrics if item.status == MISSING_INPUT]
    failed = [item for item in metrics if item.status == FAILED]
    skipped = [item for item in metrics if item.status == SKIPPED]

    lines = [
        "SQRE Multi-Scenario & Multi-Timeframe Validation Report",
        "=======================================================",
        "",
        f"Validation Name: {config.validation_name}",
        f"Generated At: {generated_at}",
        f"Scenarios Configured: {summary.scenarios_configured}",
        f"Scenarios Selected: {summary.scenarios_selected}",
        f"Scenarios Completed: {len(completed)}",
        f"Scenarios Missing Input: {len(missing)}",
        f"Scenarios Failed: {len(failed)}",
        f"Scenarios Skipped: {len(skipped)}",
        "",
        "Scenario Overview",
        "-----------------",
    ]
    if metrics:
        for item in metrics:
            lines.append(
                f"- {item.scenario_id}: status={item.status}, timeframe={item.timeframe}, "
                f"ohlc_rows={item.ohlc_rows}, structures={item.structures_detected}, states={item.states_generated}"
            )
    else:
        lines.append("- No scenarios were selected.")

    lines.extend(
        [
            "",
            "Market Structure Comparison",
            "---------------------------",
        ]
    )
    lines.extend(
        _scenario_lines(
            completed,
            lambda item: (
                f"{item.scenario_id}: structures={item.structures_detected}, "
                f"avg_duration={item.average_structure_duration:.2f}, "
                f"avg_displacement={item.average_price_displacement:.6f}, "
                f"common_direction={item.most_common_direction or 'NONE'}"
            ),
        )
    )

    lines.extend(["", "Market State Comparison", "-----------------------"])
    lines.extend(
        _scenario_lines(
            completed,
            lambda item: (
                f"{item.scenario_id}: states={item.states_generated}, unique={item.unique_states}, "
                f"common_state={item.most_common_state or 'NONE'}, avg_confidence={item.average_state_confidence:.4f}"
            ),
        )
    )

    lines.extend(["", "Transition Engine Comparison", "----------------------------"])
    lines.extend(
        _scenario_lines(
            completed,
            lambda item: (
                f"{item.scenario_id}: transitions={item.transitions_generated}, unique={item.unique_transitions}, "
                f"common_transition={item.most_common_transition or 'NONE'}, state_change_rate={item.state_change_rate:.4f}"
            ),
        )
    )

    lines.extend(["", "Research Engine Comparison", "--------------------------"])
    lines.extend(
        _scenario_lines(
            completed,
            lambda item: (
                f"{item.scenario_id}: conditions={item.conditions_evaluated}, "
                f"condition_summary_rows={item.condition_summary_rows}, "
                f"low_sample_conditions={item.low_sample_conditions_research}"
            ),
        )
    )

    lines.extend(["", "Price Outcome Research Comparison", "---------------------------------"])
    lines.extend(
        _scenario_lines(
            completed,
            lambda item: (
                f"{item.scenario_id}: outcomes={item.price_outcomes_generated}, "
                f"avg_forward_close_return_pips={item.average_forward_close_return_pips:.4f}, "
                f"direction_alignment_rate={item.direction_alignment_rate:.4f}"
            ),
        )
    )

    lines.extend(["", "Timeframe Sensitivity", "---------------------"])
    lines.extend(_timeframe_lines(completed))

    lines.extend(["", "Sample Size Review", "------------------"])
    lines.extend(_sample_lines(metrics))

    lines.extend(
        [
            "",
            "Calibration Review",
            "------------------",
            "- Compare scenario outputs before changing downstream calibration thresholds.",
            "- Review low sample size rows before interpreting scenario differences.",
            "- Confirm each timeframe uses an adequate processed dataset window.",
            "",
            "Key Findings",
            "------------",
        ]
    )
    lines.extend(_finding_lines(completed, missing, failed, skipped))

    lines.extend(
        [
            "",
            "Limitations",
            "-----------",
            "- This runner summarizes processed datasets and generated SQRE artifacts.",
            "- Missing input files are reported without stopping non-strict runs.",
            "- Results are descriptive and constrained to each processed dataset.",
            "- No execution guidance is produced.",
            "",
            "Next Steps",
            "----------",
            "- Add missing OHLC files for incomplete scenarios.",
            "- Re-run selected scenarios after adding larger datasets.",
            "- Review timeframe sensitivity before later research modules.",
            "",
        ]
    )
    return "\n".join(lines)


def _scenario_lines(metrics: list[ScenarioMetrics], formatter) -> list[str]:
    if not metrics:
        return ["- No completed scenarios available."]
    return [f"- {formatter(item)}" for item in metrics]


def _timeframe_lines(metrics: list[ScenarioMetrics]) -> list[str]:
    if not metrics:
        return ["- No completed timeframe outputs available."]
    grouped: dict[str, list[ScenarioMetrics]] = {}
    for item in metrics:
        grouped.setdefault(item.timeframe, []).append(item)
    return [
        f"- {timeframe}: scenarios={len(items)}, avg_states={_average(item.states_generated for item in items):.2f}, "
        f"avg_outcomes={_average(item.price_outcomes_generated for item in items):.2f}"
        for timeframe, items in sorted(grouped.items())
    ]


def _sample_lines(metrics: list[ScenarioMetrics]) -> list[str]:
    if not metrics:
        return ["- No scenario samples available."]
    return [
        f"- {item.scenario_id}: ohlc_rows={item.ohlc_rows}, "
        f"research_low_sample={item.low_sample_conditions_research}, "
        f"price_outcome_low_sample={item.low_sample_conditions_price_outcome}"
        for item in metrics
    ]


def _finding_lines(
    completed: list[ScenarioMetrics],
    missing: list[ScenarioMetrics],
    failed: list[ScenarioMetrics],
    skipped: list[ScenarioMetrics],
) -> list[str]:
    lines = [
        f"- Completed scenario count: {len(completed)}",
        f"- Missing input scenario count: {len(missing)}",
        f"- Failed scenario count: {len(failed)}",
        f"- Skipped scenario count: {len(skipped)}",
    ]
    if missing:
        lines.append("- Missing inputs should be added before comparing every configured timeframe.")
    if failed:
        lines.append("- Failed scenarios should be reviewed from their captured command output.")
    return lines


def _average(values) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0
