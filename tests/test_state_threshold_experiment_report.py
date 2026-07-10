from __future__ import annotations

from sqre.state_threshold_experiments.models import (
    StateThresholdExperimentMetricsRow,
    StateThresholdExperimentSummary,
)
from sqre.state_threshold_experiments.reports import (
    write_state_threshold_experiment_report,
    write_state_threshold_experiment_summary_csv,
)


def _row() -> StateThresholdExperimentMetricsRow:
    return StateThresholdExperimentMetricsRow(
        experiment_run_id="state_baseline__eurusd_h4_period_1",
        profile_id="state_baseline",
        scenario_id="eurusd_h4_period_1",
        symbol="EURUSD",
        timeframe="H4",
        status="COMPLETED",
        message="Completed successfully",
        states_generated=10,
        unique_states=4,
        most_common_state="DIRECTIONAL_DISPLACEMENT",
        most_common_state_ratio=0.4,
        directional_state_ratio=0.5,
        compression_consolidation_ratio=0.2,
        volatile_rotation_ratio=0.1,
        unclassified_rate=0.1,
        low_quality_rate=0.1,
        transitions_generated=9,
        unique_transitions=3,
        most_common_transition="A_TO_B",
        state_change_rate=0.5,
        direction_change_rate=0.2,
        average_transition_stability=0.7,
        conditions_evaluated=8,
        research_low_sample_rate=0.25,
        price_outcome_summary_rows=8,
        price_outcome_low_sample_rate=0.25,
        average_forward_range_pips=12.0,
        direction_alignment_rate=0.5,
    )


def test_write_state_threshold_experiment_summary_csv(tmp_path) -> None:
    output = tmp_path / "summary.csv"

    write_state_threshold_experiment_summary_csv(output, [_row()])

    text = output.read_text(encoding="utf-8")
    assert "Experiment_Run_ID" in text
    assert "Relative_Forward_Range_Change_vs_Baseline" in text


def test_write_state_threshold_experiment_report_sections_and_guardrails(tmp_path) -> None:
    output = tmp_path / "report.txt"
    summary = StateThresholdExperimentSummary(
        experiment_name="state_threshold_experiments_v1",
        runs_configured=1,
        runs_completed=1,
        runs_missing_input=0,
        runs_failed=0,
        summary_rows=1,
        output_path=tmp_path / "summary.csv",
        report_path=output,
    )

    write_state_threshold_experiment_report(output, summary, [_row()])

    text = output.read_text(encoding="utf-8")
    assert "SQRE State Threshold Experiment Report" in text
    assert "Experiment Scope" in text
    assert "Profile Overview" in text
    assert "State Distribution Comparison" in text
    assert "Transition Sensitivity" in text
    assert "Research and Price Outcome Sensitivity" in text
    assert "Do Not Change Yet" in text
    assert "No profile ranking is produced." in text
    assert "No operational market action logic was added." in text
