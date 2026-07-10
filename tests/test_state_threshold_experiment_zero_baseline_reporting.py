from __future__ import annotations

from sqre.state_threshold_experiments.metrics import apply_baseline_comparisons
from sqre.state_threshold_experiments.models import StateThresholdExperimentMetricsRow


def _row(
    profile_id: str,
    *,
    unclassified_rate: float,
    directional_state_ratio: float = 0.5,
    average_forward_range_pips: float = 10.0,
    unique_states: int = 4,
) -> StateThresholdExperimentMetricsRow:
    return StateThresholdExperimentMetricsRow(
        experiment_run_id=f"{profile_id}__eurusd_d1_period_1",
        profile_id=profile_id,
        scenario_id="eurusd_d1_period_1",
        symbol="EURUSD",
        timeframe="D1",
        status="COMPLETED",
        message="Completed successfully",
        unclassified_rate=unclassified_rate,
        directional_state_ratio=directional_state_ratio,
        average_forward_range_pips=average_forward_range_pips,
        unique_states=unique_states,
    )


def _compare(baseline: StateThresholdExperimentMetricsRow, profile: StateThresholdExperimentMetricsRow):
    rows = apply_baseline_comparisons([baseline, profile])
    return next(row for row in rows if row.profile_id == profile.profile_id)


def test_zero_baseline_and_zero_current_reports_stable_at_zero() -> None:
    compared = _compare(
        _row("state_baseline", unclassified_rate=0.0),
        _row("balanced_high_tf", unclassified_rate=0.0),
    )

    assert compared.absolute_unclassified_rate_change_vs_baseline == 0.0
    assert "unclassified rate stable at zero" in compared.experiment_notes


def test_zero_baseline_and_positive_current_reports_increased_from_zero() -> None:
    compared = _compare(
        _row("state_baseline", unclassified_rate=0.0),
        _row("balanced_high_tf", unclassified_rate=0.0811),
    )

    assert compared.relative_unclassified_rate_vs_baseline == 0.0
    assert compared.absolute_unclassified_rate_change_vs_baseline == 0.0811
    assert "unclassified rate increased from zero" in compared.experiment_notes
    assert "unclassified rate stable" not in compared.experiment_notes


def test_positive_baseline_and_zero_current_reports_decreased_to_zero() -> None:
    compared = _compare(
        _row("state_baseline", unclassified_rate=0.05),
        _row("balanced_high_tf", unclassified_rate=0.0),
    )

    assert compared.relative_unclassified_rate_vs_baseline == -1.0
    assert compared.absolute_unclassified_rate_change_vs_baseline == -0.05
    assert "unclassified rate decreased to zero" in compared.experiment_notes


def test_positive_baseline_and_positive_current_keeps_relative_comparison() -> None:
    compared = _compare(
        _row("state_baseline", unclassified_rate=0.05, directional_state_ratio=0.50),
        _row("balanced_high_tf", unclassified_rate=0.10, directional_state_ratio=0.25),
    )

    assert compared.relative_unclassified_rate_vs_baseline == 1.0
    assert compared.absolute_unclassified_rate_change_vs_baseline == 0.05
    assert compared.relative_directional_state_ratio_vs_baseline == -0.5
    assert "unclassified rate increased" in compared.experiment_notes
