from pathlib import Path

import pandas as pd

from sqre.calibration_experiments.metrics import apply_baseline_comparisons, collect_experiment_metrics
from sqre.calibration_experiments.models import ExperimentMetricsRow, ExperimentRun, ExperimentRunResult


def _run(tmp_path: Path) -> ExperimentRun:
    output_dir = tmp_path / "out"
    return ExperimentRun(
        experiment_run_id="duration_baseline__scenario",
        experiment_type="DURATION",
        experiment_id="duration_baseline",
        scenario_id="scenario",
        symbol="EURUSD",
        timeframe="H4",
        ohlc_path=tmp_path / "ohlc.csv",
        max_structure_duration_seconds=100,
        minimum_sample_size=5,
        forward_candles=[3, 6, 12],
        output_dir=output_dir,
        processed_dir=output_dir / "processed",
        research_dir=output_dir / "research",
        reports_dir=output_dir / "reports",
    )


def _result(run: ExperimentRun) -> ExperimentRunResult:
    return ExperimentRunResult(
        experiment_run_id=run.experiment_run_id,
        experiment_type=run.experiment_type,
        experiment_id=run.experiment_id,
        scenario_id=run.scenario_id,
        symbol=run.symbol,
        timeframe=run.timeframe,
        status="COMPLETED",
        message="Completed successfully",
        started_at="2026-01-01T00:00:00+00:00",
        completed_at="2026-01-01T00:01:00+00:00",
        output_dir=run.output_dir,
    )


def test_collect_experiment_metrics_from_synthetic_outputs(tmp_path: Path):
    run = _run(tmp_path)
    run.processed_dir.mkdir(parents=True)
    run.research_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {"Date": "2026-01-01 00:00:00", "Open": 1, "High": 2, "Low": 0, "Close": 1, "Volume": 0},
            {"Date": "2026-01-01 01:00:00", "Open": 1, "High": 2, "Low": 0, "Close": 1, "Volume": 0},
        ]
    ).to_csv(run.ohlc_path, index=False)
    pd.DataFrame(
        [
            {"duration_seconds": 40, "price_displacement": 0.1, "direction": "UP", "persistence_index": 0.5},
            {"duration_seconds": 60, "price_displacement": 0.3, "direction": "DOWN", "persistence_index": 0.7},
        ]
    ).to_csv(run.processed_dir / "structures.csv", index=False)
    pd.DataFrame(
        [
            {"market_state": "DIRECTIONAL_DISPLACEMENT", "state_confidence": 0.8},
            {"market_state": "DIRECTIONAL_DISPLACEMENT", "state_confidence": 0.7},
            {"market_state": "NEUTRAL_COMPRESSION", "state_confidence": 0.6},
        ]
    ).to_csv(run.processed_dir / "market_states.csv", index=False)
    pd.DataFrame(
        [
            {"transition_label": "A_TO_B", "state_changed": "True", "direction_changed": "False"},
            {"transition_label": "A_TO_C", "state_changed": "False", "direction_changed": "True"},
        ]
    ).to_csv(run.processed_dir / "state_transitions.csv", index=False)
    pd.DataFrame(
        [
            {"condition_id": "c1", "low_sample_size": "True"},
            {"condition_id": "c2", "low_sample_size": "False"},
        ]
    ).to_csv(run.research_dir / "condition_summaries.csv", index=False)
    pd.DataFrame([{"id": 1}, {"id": 2}]).to_csv(run.research_dir / "price_outcomes.csv", index=False)
    pd.DataFrame(
        [
            {
                "condition_id": "c1",
                "low_sample_size": True,
                "average_forward_close_return_pips": 1.0,
                "median_forward_close_return_pips": 0.5,
                "average_forward_range_pips": 10.0,
                "average_outcome_magnitude_pips": 5.0,
                "direction_alignment_rate": 0.6,
            },
            {
                "condition_id": "c2",
                "low_sample_size": False,
                "average_forward_close_return_pips": 3.0,
                "median_forward_close_return_pips": 1.5,
                "average_forward_range_pips": 12.0,
                "average_outcome_magnitude_pips": 7.0,
                "direction_alignment_rate": 0.8,
            },
        ]
    ).to_csv(run.research_dir / "condition_price_outcome_summary.csv", index=False)
    pd.DataFrame([{"bucket": "A"}]).to_csv(run.research_dir / "price_outcome_distributions.csv", index=False)

    row = collect_experiment_metrics(run, _result(run))

    assert row.ohlc_rows == 2
    assert row.structures_detected == 2
    assert row.average_structure_duration == 50.0
    assert row.duration_utilization_ratio == 0.5
    assert row.states_generated == 3
    assert row.most_common_state_ratio == 2 / 3
    assert row.directional_state_ratio == 2 / 3
    assert row.research_low_sample_rate == 0.5
    assert row.price_outcome_low_sample_rate == 0.5
    assert row.average_forward_range_pips == 11.0


def test_collect_experiment_metrics_handles_missing_optional_columns(tmp_path: Path):
    run = _run(tmp_path)
    run.processed_dir.mkdir(parents=True)
    run.research_dir.mkdir(parents=True)
    pd.DataFrame([{"Date": "2026-01-01"}]).to_csv(run.ohlc_path, index=False)

    row = collect_experiment_metrics(run, _result(run))

    assert row.structures_detected == 0
    assert row.conditions_evaluated == 0
    assert row.price_outcome_low_sample_rate == 0.0


def test_apply_baseline_comparisons_adds_relative_changes():
    baseline = ExperimentMetricsRow(
        experiment_run_id="duration_baseline__scenario",
        experiment_type="DURATION",
        experiment_id="duration_baseline",
        scenario_id="scenario",
        symbol="EURUSD",
        timeframe="H4",
        status="COMPLETED",
        message="ok",
        structures_detected=10,
        average_structure_duration=100,
        unique_states=5,
        average_forward_range_pips=20,
    )
    expanded = ExperimentMetricsRow(
        experiment_run_id="duration_expanded__scenario",
        experiment_type="DURATION",
        experiment_id="duration_expanded",
        scenario_id="scenario",
        symbol="EURUSD",
        timeframe="H4",
        status="COMPLETED",
        message="ok",
        structures_detected=15,
        average_structure_duration=120,
        unique_states=4,
        average_forward_range_pips=22,
    )

    rows = apply_baseline_comparisons([baseline, expanded])

    assert rows[1].relative_structure_count_change_vs_baseline == 0.5
    assert rows[1].relative_duration_change_vs_baseline == 0.2
    assert rows[1].relative_state_diversity_change_vs_baseline == -0.2
    assert rows[1].relative_forward_range_change_vs_baseline == 0.1
