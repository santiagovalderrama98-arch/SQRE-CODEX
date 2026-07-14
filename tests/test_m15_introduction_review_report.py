from pathlib import Path

import pandas as pd

from sqre.m15_introduction_review.models import M15ReviewFinding, M15ReviewResult, M15ReviewRow
from sqre.m15_introduction_review.reports import write_m15_review_report, write_m15_review_summary_csv


def test_summary_writer_outputs_required_columns(tmp_path):
    output = tmp_path / "m15_review.csv"

    write_m15_review_summary_csv(output, [_review_row()])

    frame = pd.read_csv(output)
    assert list(frame["Timeframe"]) == ["M15"]
    assert "Context_Interpretation" in frame.columns
    assert "M15_Diagnostic_Profile" in frame.columns


def test_report_writer_outputs_required_sections_and_safe_language(tmp_path):
    report = tmp_path / "m15_review.txt"
    result = M15ReviewResult(
        input_summary="summary.csv",
        master_summary="master.csv",
        rows_loaded=7,
        scenarios_reviewed=7,
        output_path=tmp_path / "summary.csv",
        report_path=report,
        rows=[_review_row()],
    )
    findings = [M15ReviewFinding("DIAGNOSTIC_PROFILE", "Candidate intraday research timeframe", "Review M15 context.")]

    write_m15_review_report(report, result, findings)

    text = report.read_text(encoding="utf-8")
    assert "SQRE M15 Timeframe Introduction Review" in text
    assert "Executive Diagnostic Summary" in text
    assert "M15 vs M5/H1 Context" in text
    assert "No comparative ordering is produced." in text
    assert not _contains_forbidden_language(text)


def _review_row() -> M15ReviewRow:
    return M15ReviewRow(
        timeframe="M15",
        scenario_count=7,
        completed_scenario_count=7,
        failed_scenario_count=0,
        missing_input_count=0,
        scenario_ids="eurusd_m15_period_1",
        total_ohlc_rows=700,
        average_ohlc_rows=100,
        average_structures_detected=10,
        min_structures_detected=8,
        max_structures_detected=12,
        structure_count_range=4,
        structure_count_cv=0.1,
        average_structure_duration=7200,
        average_duration_utilization_ratio=0.25,
        duration_reference_seconds=28800,
        average_unique_states=5,
        min_unique_states=4,
        max_unique_states=6,
        state_diversity_range=2,
        most_common_state_mode="DIRECTIONAL_DRIFT",
        directional_displacement_total=10,
        directional_expansion_total=5,
        directional_drift_total=3,
        volatile_rotation_total=2,
        complex_consolidation_total=1,
        low_quality_structure_total=0,
        unclassified_total=0,
        average_directional_state_ratio=0.2,
        average_complex_consolidation_ratio=0.1,
        average_volatile_rotation_ratio=0.05,
        average_low_quality_rate=0.0,
        average_unclassified_rate=0.0,
        average_forward_range_pips=8,
        min_forward_range_pips=6,
        max_forward_range_pips=10,
        forward_range_cv=0.1,
        average_outcome_magnitude_pips=4,
        average_direction_alignment_rate=0.4,
        average_low_sample_conditions_research=4,
        average_low_sample_conditions_price_outcome=3,
        max_low_sample_conditions_research=6,
        max_low_sample_conditions_price_outcome=5,
        structure_stability_flag="STABLE",
        duration_utilization_flag="MODERATE",
        state_diversity_flag="BALANCED_DIVERSITY",
        low_sample_pressure_flag="MODERATE",
        forward_range_stability_flag="STABLE",
        m15_diagnostic_profile="Candidate intraday research timeframe",
        recommended_follow_up="Review M15 against additional periods and compare with H1/M5 context.",
        m5_average_structures_context=8,
        h1_average_structures_context=12,
        m5_average_unique_states_context=4,
        h1_average_unique_states_context=6,
        m5_low_sample_context=8,
        h1_low_sample_context=10,
        context_interpretation="M15 context is available against M5 and H1 descriptive baselines.",
    )


def _contains_forbidden_language(text: str) -> bool:
    forbidden = [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "take profit",
        "stop loss",
        "profitable",
        "best timeframe",
        "ranking",
        "should trade",
        "predicts",
        "optimal",
    ]
    lower = text.lower()
    return any(term in lower for term in forbidden)
