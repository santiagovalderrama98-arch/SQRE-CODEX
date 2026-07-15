"""Report and CSV writers for D1 regime outcome review."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from sqre.d1_regime_outcome_review.loader import optional_input_file_status
from sqre.d1_regime_outcome_review.models import (
    ConditionLabelSummary,
    ConditionQualityInventoryRow,
    D1OutcomeReviewSummary,
    D1RegimeOutcomeReviewResult,
    DispersionSummary,
    SampleAdequacySummary,
)


INVENTORY_COLUMNS = [
    "Condition_Type",
    "Condition_Label",
    "Forward_Window",
    "Regime_Count",
    "Regimes_Present",
    "Scenario_Count",
    "Total_Sample_Size",
    "Average_Sample_Size_Per_Regime",
    "Average_Forward_Range_Pips",
    "Average_Outcome_Magnitude_Pips",
    "Average_Direction_Alignment_Rate",
    "Forward_Range_CV",
    "Outcome_Magnitude_CV",
    "Direction_Alignment_CV",
    "Sample_Adequacy_Class",
    "Regime_Coverage_Class",
    "Dispersion_Class",
    "Sensitivity_Class",
    "Condition_Research_Class",
    "Condition_Review_Diagnostic",
    "Recommended_Follow_Up",
]

STATE_SUMMARY_COLUMNS = [
    "Condition_Label",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Regime_Sensitive_Profile_Count",
    "Low_Sample_Profile_Count",
    "Limited_Coverage_Profile_Count",
    "Average_Total_Sample_Size",
    "Average_Regime_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Dominant_Condition_Research_Class",
    "State_Condition_Diagnostic",
    "Recommended_Follow_Up",
]

TRANSITION_SUMMARY_COLUMNS = [
    "Condition_Label",
    "Profile_Count",
    "Research_Ready_Profile_Count",
    "Regime_Sensitive_Profile_Count",
    "Low_Sample_Profile_Count",
    "Limited_Coverage_Profile_Count",
    "Average_Total_Sample_Size",
    "Average_Regime_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Dominant_Condition_Research_Class",
    "Transition_Condition_Diagnostic",
    "Recommended_Follow_Up",
]

DISPERSION_COLUMNS = [
    "Condition_Type",
    "Profile_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Low_Dispersion_Profile_Count",
    "Moderate_Dispersion_Profile_Count",
    "High_Dispersion_Profile_Count",
    "Stable_Sensitivity_Profile_Count",
    "Moderate_Sensitivity_Profile_Count",
    "High_Sensitivity_Profile_Count",
    "Outcome_Dispersion_Diagnostic",
]

SAMPLE_COLUMNS = [
    "Scope",
    "Profile_Count",
    "Adequate_Profile_Count",
    "Low_Sample_Profile_Count",
    "Limited_Coverage_Profile_Count",
    "Research_Ready_Profile_Count",
    "Regime_Sensitive_Profile_Count",
    "Adequate_Profile_Ratio",
    "Low_Sample_Profile_Ratio",
    "Limited_Coverage_Profile_Ratio",
    "Research_Ready_Profile_Ratio",
    "Sample_Adequacy_Diagnostic",
]

SUMMARY_COLUMNS = [
    "Timeframe",
    "Input_Profile_Count",
    "Research_Ready_Profile_Count",
    "Regime_Sensitive_Profile_Count",
    "Low_Sample_Profile_Count",
    "Limited_Coverage_Profile_Count",
    "High_Dispersion_Profile_Count",
    "State_Profile_Count",
    "Transition_Profile_Count",
    "Research_Ready_State_Profile_Count",
    "Research_Ready_Transition_Profile_Count",
    "Average_Forward_Range_CV",
    "Average_Outcome_Magnitude_CV",
    "Average_Direction_Alignment_Rate",
    "Sample_Adequacy_Profile",
    "Outcome_Dispersion_Profile",
    "Regime_Sensitivity_Profile",
    "D1_Outcome_Review_Diagnostic",
    "Recommended_Follow_Up",
]


def write_review_outputs(result: D1RegimeOutcomeReviewResult) -> D1RegimeOutcomeReviewResult:
    result.output_dir.mkdir(parents=True, exist_ok=True)
    result.report_path.parent.mkdir(parents=True, exist_ok=True)

    _write_rows(result.output_dir / "d1_condition_quality_inventory.csv", result.inventory_rows, INVENTORY_COLUMNS)
    _write_profile_subset(
        result.output_dir / "d1_research_ready_condition_profiles.csv",
        result.research_ready_profiles,
        "Research_Readiness_Rationale",
    )
    _write_profile_subset(
        result.output_dir / "d1_regime_sensitive_condition_profiles.csv",
        result.regime_sensitive_profiles,
        "Regime_Sensitivity_Rationale",
    )
    _write_profile_subset(
        result.output_dir / "d1_low_sample_condition_profiles.csv",
        result.low_sample_profiles,
        "Sample_Review_Rationale",
    )
    _write_profile_subset(
        result.output_dir / "d1_limited_coverage_condition_profiles.csv",
        result.limited_coverage_profiles,
        "Coverage_Review_Rationale",
    )
    _write_rows(result.output_dir / "d1_state_condition_quality_summary.csv", result.state_summaries, STATE_SUMMARY_COLUMNS)
    _write_rows(
        result.output_dir / "d1_transition_condition_quality_summary.csv",
        result.transition_summaries,
        TRANSITION_SUMMARY_COLUMNS,
    )
    _write_rows(result.output_dir / "d1_outcome_dispersion_summary.csv", result.dispersion_summaries, DISPERSION_COLUMNS)
    _write_rows(result.output_dir / "d1_sample_adequacy_summary.csv", result.sample_adequacy_summaries, SAMPLE_COLUMNS)
    _write_rows(
        result.output_dir / "d1_regime_outcome_review_summary.csv",
        [result.review_summary] if result.review_summary else [],
        SUMMARY_COLUMNS,
    )
    result.report_path.write_text(build_report_text(result), encoding="utf-8")
    return result


def build_report_text(result: D1RegimeOutcomeReviewResult) -> str:
    summary = result.review_summary
    optional_inputs = optional_input_file_status(result.input_dir)
    lines = [
        "SQRE D1 Regime Outcome Dispersion & Sample Adequacy Review",
        "============================================================",
        "",
        f"Generated At: {datetime.now(timezone.utc).isoformat()}",
        f"Input Directory: {result.input_dir}",
        f"Output Directory: {result.output_dir}",
        f"Profiles Loaded: {result.profiles_loaded}",
        "",
        "Executive Diagnostic Summary",
        "----------------------------",
    ]
    if summary:
        lines.extend(
            [
                f"Timeframe: {summary.timeframe}",
                f"Input Profile Count: {summary.input_profile_count}",
                f"Research-Ready Profile Count: {summary.research_ready_profile_count}",
                f"Regime-Sensitive Profile Count: {summary.regime_sensitive_profile_count}",
                f"Low-Sample Profile Count: {summary.low_sample_profile_count}",
                f"Limited-Coverage Profile Count: {summary.limited_coverage_profile_count}",
                f"Average Forward Range CV: {_fmt(summary.average_forward_range_cv)}",
                f"Average Outcome Magnitude CV: {_fmt(summary.average_outcome_magnitude_cv)}",
                f"Average Direction Alignment Rate: {_fmt(summary.average_direction_alignment_rate)}",
                f"Sample Adequacy Profile: {summary.sample_adequacy_profile}",
                f"Outcome Dispersion Profile: {summary.outcome_dispersion_profile}",
                f"Regime Sensitivity Profile: {summary.regime_sensitivity_profile}",
                f"Diagnostic: {summary.d1_outcome_review_diagnostic}",
            ]
        )
    else:
        lines.append("No profiles were available for review.")
    lines.extend(
        [
            "",
            "Condition Quality Overview",
            "--------------------------",
            f"Inventory Rows: {len(result.inventory_rows)}",
            f"Optional Input Availability: {_optional_status_text(optional_inputs)}",
            "",
            "Research-Ready Descriptive Profiles",
            "------------------------------------",
            f"Profiles: {len(result.research_ready_profiles)}",
            _top_profiles(result.research_ready_profiles),
            "",
            "Regime-Sensitive Profiles",
            "-------------------------",
            f"Profiles: {len(result.regime_sensitive_profiles)}",
            _top_profiles(result.regime_sensitive_profiles),
            "",
            "Low-Sample / Limited-Coverage Review",
            "------------------------------------",
            f"Low-Sample Profiles: {len(result.low_sample_profiles)}",
            f"Limited-Coverage Profiles: {len(result.limited_coverage_profiles)}",
            "",
            "State Condition Review",
            "----------------------",
            _label_summary_text(result.state_summaries, "state_condition_diagnostic"),
            "",
            "Transition Condition Review",
            "---------------------------",
            _label_summary_text(result.transition_summaries, "transition_condition_diagnostic"),
            "",
            "Outcome Dispersion Review",
            "-------------------------",
            _dispersion_text(result.dispersion_summaries),
            "",
            "Research Readiness Assessment",
            "-----------------------------",
            _sample_text(result.sample_adequacy_summaries),
            "",
            "Potential Follow-Up Areas",
            "-------------------------",
            "- D1 state outcome deep dive using research-ready profiles",
            "- D1 transition outcome regime-sensitive review",
            "- H4 state/transition outcome deep dive",
            "- H4/D1 condition-family aggregation",
            "- Research reference-store design",
            "",
            "Do Not Change Yet",
            "-----------------",
            "- Do not change production defaults.",
            "- Do not change Market State thresholds.",
            "- Do not change Event Detection or Market Structure defaults.",
            "- Do not add operational decision logic.",
            "- No comparative ordering is produced.",
            "",
            "Limitations",
            "-----------",
            "- This review is descriptive and depends on the normalized D1 research inputs.",
            "- Low sample profiles require sample adequacy review before broader aggregation.",
            "- Regime-sensitive profiles require separate descriptive review before aggregation.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_profile_subset(path: Path, rows: list[ConditionQualityInventoryRow], rationale_column: str) -> None:
    records = [_row_record(row, INVENTORY_COLUMNS) | {rationale_column: row.condition_review_diagnostic} for row in rows]
    _write_records(path, records, INVENTORY_COLUMNS + [rationale_column])


def _write_rows(path: Path, rows: Iterable[object], columns: list[str]) -> None:
    records = [_row_record(row, columns) for row in rows]
    _write_records(path, records, columns)


def _write_records(path: Path, records: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records, columns=columns).to_csv(path, index=False)


def _row_record(row: object, columns: list[str]) -> dict[str, object]:
    raw = asdict(row)
    return {column: raw.get(_field_name(column), "") for column in columns}


def _field_name(column: str) -> str:
    return column.lower()


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _optional_status_text(status: dict[str, bool]) -> str:
    if not status:
        return "none"
    return ", ".join(f"{name}={'present' if present else 'missing'}" for name, present in sorted(status.items()))


def _top_profiles(rows: list[ConditionQualityInventoryRow]) -> str:
    if not rows:
        return "No profiles in this category."
    lines = []
    for row in rows[:5]:
        lines.append(
            "- "
            f"{row.condition_type} | {row.condition_label} | FW={row.forward_window} | "
            f"sample={row.total_sample_size} | dispersion={row.dispersion_class} | "
            f"sensitivity={row.sensitivity_class}"
        )
    return "\n".join(lines)


def _label_summary_text(rows: list[ConditionLabelSummary], diagnostic_field: str) -> str:
    if not rows:
        return "No condition summaries in this category."
    lines = []
    for row in rows[:8]:
        diagnostic = getattr(row, diagnostic_field)
        lines.append(
            "- "
            f"{row.condition_label}: profiles={row.profile_count}, "
            f"ready={row.research_ready_profile_count}, sensitive={row.regime_sensitive_profile_count}, "
            f"diagnostic={diagnostic}"
        )
    return "\n".join(lines)


def _dispersion_text(rows: list[DispersionSummary]) -> str:
    if not rows:
        return "No dispersion summaries available."
    return "\n".join(
        "- "
        f"{row.condition_type}: profiles={row.profile_count}, high={row.high_dispersion_profile_count}, "
        f"avg_range_cv={_fmt(row.average_forward_range_cv)}, avg_magnitude_cv={_fmt(row.average_outcome_magnitude_cv)}"
        for row in rows
    )


def _sample_text(rows: list[SampleAdequacySummary]) -> str:
    if not rows:
        return "No sample adequacy summaries available."
    return "\n".join(
        "- "
        f"{row.scope}: profiles={row.profile_count}, adequate_ratio={_fmt(row.adequate_profile_ratio)}, "
        f"low_sample_ratio={_fmt(row.low_sample_profile_ratio)}, ready_ratio={_fmt(row.research_ready_profile_ratio)}"
        for row in rows
    )
