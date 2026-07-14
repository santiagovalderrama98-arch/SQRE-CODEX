"""Reports for M15 introduction review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from sqre.m15_introduction_review.models import M15ReviewFinding, M15ReviewResult, M15ReviewRow


SUMMARY_COLUMNS = [
    "Timeframe",
    "Scenario_Count",
    "Completed_Scenario_Count",
    "Failed_Scenario_Count",
    "Missing_Input_Count",
    "Scenario_IDs",
    "Total_OHLC_Rows",
    "Average_OHLC_Rows",
    "Average_Structures_Detected",
    "Min_Structures_Detected",
    "Max_Structures_Detected",
    "Structure_Count_Range",
    "Structure_Count_CV",
    "Average_Structure_Duration",
    "Average_Duration_Utilization_Ratio",
    "Duration_Reference_Seconds",
    "Average_Unique_States",
    "Min_Unique_States",
    "Max_Unique_States",
    "State_Diversity_Range",
    "Most_Common_State_Mode",
    "Directional_Displacement_Total",
    "Directional_Expansion_Total",
    "Directional_Drift_Total",
    "Volatile_Rotation_Total",
    "Complex_Consolidation_Total",
    "Low_Quality_Structure_Total",
    "Unclassified_Total",
    "Average_Directional_State_Ratio",
    "Average_Complex_Consolidation_Ratio",
    "Average_Volatile_Rotation_Ratio",
    "Average_Low_Quality_Rate",
    "Average_Unclassified_Rate",
    "Average_Forward_Range_Pips",
    "Min_Forward_Range_Pips",
    "Max_Forward_Range_Pips",
    "Forward_Range_CV",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Average_Low_Sample_Conditions_Research",
    "Average_Low_Sample_Conditions_Price_Outcome",
    "Max_Low_Sample_Conditions_Research",
    "Max_Low_Sample_Conditions_Price_Outcome",
    "Structure_Stability_Flag",
    "Duration_Utilization_Flag",
    "State_Diversity_Flag",
    "Low_Sample_Pressure_Flag",
    "Forward_Range_Stability_Flag",
    "M15_Diagnostic_Profile",
    "Recommended_Follow_Up",
    "M5_Average_Structures_Context",
    "H1_Average_Structures_Context",
    "M5_Average_Unique_States_Context",
    "H1_Average_Unique_States_Context",
    "M5_Low_Sample_Context",
    "H1_Low_Sample_Context",
    "Context_Interpretation",
]


def write_m15_review_summary_csv(path: Path | str, rows: list[M15ReviewRow]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_summary_row(row) for row in rows], columns=SUMMARY_COLUMNS).to_csv(output_path, index=False)


def write_m15_review_report(
    path: Path | str,
    result: M15ReviewResult,
    findings: list[M15ReviewFinding],
) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(result, findings), encoding="utf-8")


def _summary_row(row: M15ReviewRow) -> dict[str, Any]:
    raw = asdict(row)
    return {_column: _blank_none(raw[_snake(_column)]) for _column in SUMMARY_COLUMNS}


def _build_report(result: M15ReviewResult, findings: list[M15ReviewFinding]) -> str:
    rows = result.rows
    lines = [
        "SQRE M15 Timeframe Introduction Review",
        "======================================",
        "",
        "Generated At",
        "------------",
        datetime.now(timezone.utc).isoformat(),
        "",
        "Input Summary",
        "-------------",
        result.input_summary,
        "",
        "Rows Loaded",
        "-----------",
        str(result.rows_loaded),
        "",
        "Scenarios Reviewed",
        "------------------",
        str(result.scenarios_reviewed),
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
    ]
    lines.extend(_executive_lines(rows))
    lines.extend(["", "Scenario Coverage", "-----------------"])
    lines.extend(_coverage_lines(rows))
    lines.extend(["", "M15 Structural Overview", "-----------------------"])
    lines.extend(_structural_lines(rows))
    lines.extend(["", "M15 State Distribution Review", "-----------------------------"])
    lines.extend(_state_lines(rows))
    lines.extend(["", "M15 Price Outcome Context", "-------------------------"])
    lines.extend(_price_outcome_lines(rows))
    lines.extend(["", "M15 vs M5/H1 Context", "--------------------"])
    lines.extend(_context_lines(rows, result.master_summary))
    lines.extend(["", "Diagnostic Findings", "-------------------"])
    lines.extend(_finding_lines(findings))
    lines.extend(
        [
            "",
            "Potential Follow-Up Areas",
            "-------------------------",
            "- M15 duration calibration experiments",
            "- M15 vs H1/M5 comparative diagnostic review",
            "- M15 price outcome aggregation",
            "- Continued H4/D1 monitoring as higher-timeframe context",
            "",
            "Do Not Change Yet",
            "-----------------",
            "- No production defaults were modified.",
            "- No thresholds were modified.",
            "- No production taxonomy was modified.",
            "- No Decision Engine was added.",
            "- No operational logic was added.",
            "",
            "Limitations",
            "-----------",
            "- Review depends on available M15 validation summaries.",
            "- Findings are descriptive.",
            "- No comparative ordering is produced.",
            "- No production calibration action is made.",
            "",
        ]
    )
    return "\n".join(lines)


def _executive_lines(rows: list[M15ReviewRow]) -> list[str]:
    if not rows:
        return ["- No M15 rows available."]
    return [f"- M15: {row.m15_diagnostic_profile}; follow_up={row.recommended_follow_up}" for row in rows]


def _coverage_lines(rows: list[M15ReviewRow]) -> list[str]:
    if not rows:
        return ["- No scenario coverage available."]
    row = rows[0]
    return [
        f"- Scenario count: {row.scenario_count}",
        f"- Completed scenarios: {row.completed_scenario_count}",
        f"- Failed scenarios: {row.failed_scenario_count}",
        f"- Missing input scenarios: {row.missing_input_count}",
        f"- Scenario IDs: {row.scenario_ids}",
    ]


def _structural_lines(rows: list[M15ReviewRow]) -> list[str]:
    if not rows:
        return ["- No structural overview available."]
    row = rows[0]
    return [
        f"- Average structures detected: {row.average_structures_detected:.4f}",
        f"- Structure count range: {row.structure_count_range}",
        f"- Structure count CV: {row.structure_count_cv:.4f}",
        f"- Average structure duration: {row.average_structure_duration:.4f}",
        f"- Duration utilization: {row.average_duration_utilization_ratio:.4f}",
        f"- Structure stability flag: {row.structure_stability_flag}",
        f"- Duration utilization flag: {row.duration_utilization_flag}",
    ]


def _state_lines(rows: list[M15ReviewRow]) -> list[str]:
    if not rows:
        return ["- No state distribution review available."]
    row = rows[0]
    return [
        f"- Average unique states: {row.average_unique_states:.4f}",
        f"- State diversity range: {row.state_diversity_range}",
        f"- Most common state mode: {row.most_common_state_mode or 'NONE'}",
        f"- Average directional state ratio: {row.average_directional_state_ratio:.4f}",
        f"- Average complex consolidation ratio: {row.average_complex_consolidation_ratio:.4f}",
        f"- Average volatile rotation ratio: {row.average_volatile_rotation_ratio:.4f}",
        f"- State diversity flag: {row.state_diversity_flag}",
    ]


def _price_outcome_lines(rows: list[M15ReviewRow]) -> list[str]:
    if not rows:
        return ["- No price outcome context available."]
    row = rows[0]
    return [
        f"- Average forward range pips: {row.average_forward_range_pips:.4f}",
        f"- Forward range CV: {row.forward_range_cv:.4f}",
        f"- Average outcome magnitude pips: {row.average_outcome_magnitude_pips:.4f}",
        f"- Direction alignment rate: {row.average_direction_alignment_rate:.4f}",
        f"- Low sample pressure flag: {row.low_sample_pressure_flag}",
        f"- Forward range stability flag: {row.forward_range_stability_flag}",
    ]


def _context_lines(rows: list[M15ReviewRow], master_summary: str) -> list[str]:
    if not rows:
        return ["- No M5/H1 context available."]
    row = rows[0]
    return [
        f"- Master summary: {master_summary or 'not provided'}",
        f"- M5 average structures context: {_format_optional(row.m5_average_structures_context)}",
        f"- H1 average structures context: {_format_optional(row.h1_average_structures_context)}",
        f"- M5 average unique states context: {_format_optional(row.m5_average_unique_states_context)}",
        f"- H1 average unique states context: {_format_optional(row.h1_average_unique_states_context)}",
        f"- M5 low sample context: {_format_optional(row.m5_low_sample_context)}",
        f"- H1 low sample context: {_format_optional(row.h1_low_sample_context)}",
        f"- Interpretation: {row.context_interpretation}",
    ]


def _finding_lines(findings: list[M15ReviewFinding]) -> list[str]:
    if not findings:
        return ["- No findings generated."]
    return [f"- type={finding.finding_type}, flag={finding.flag}. {finding.message}" for finding in findings]


def _format_optional(value: float | None) -> str:
    if value is None:
        return "not available"
    return f"{value:.4f}"


def _snake(column: str) -> str:
    return column.lower()


def _blank_none(value: Any) -> Any:
    if value is None:
        return ""
    return value
