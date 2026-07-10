from __future__ import annotations

from pathlib import Path

import pandas as pd

from sqre.state_threshold_experiments.metrics import (
    apply_baseline_comparisons,
    collect_state_threshold_metrics,
)
from sqre.state_threshold_experiments.models import (
    StateThresholdExperimentRun,
    StateThresholdExperimentRunResult,
)


def _run(tmp_path: Path, profile_id: str = "state_baseline") -> StateThresholdExperimentRun:
    return StateThresholdExperimentRun(
        experiment_run_id=f"{profile_id}__eurusd_h4_period_1",
        profile_id=profile_id,
        scenario_id="eurusd_h4_period_1",
        symbol="EURUSD",
        timeframe="H4",
        ohlc_path=tmp_path / profile_id / "ohlc.csv",
        state_config_path=Path("configs/validation/state_threshold_profiles.yaml"),
        max_structure_duration_seconds=604800,
        minimum_sample_size=5,
        forward_candles=[3, 6, 12],
        output_dir=tmp_path / profile_id,
        processed_dir=tmp_path / profile_id / "processed",
        research_dir=tmp_path / profile_id / "research",
        reports_dir=tmp_path / profile_id / "reports",
    )


def _result(run: StateThresholdExperimentRun) -> StateThresholdExperimentRunResult:
    return StateThresholdExperimentRunResult(
        experiment_run_id=run.experiment_run_id,
        profile_id=run.profile_id,
        scenario_id=run.scenario_id,
        symbol=run.symbol,
        timeframe=run.timeframe,
        status="COMPLETED",
        message="Completed successfully",
        started_at="2026-01-01T00:00:00+00:00",
        completed_at="2026-01-01T00:01:00+00:00",
        output_dir=run.output_dir,
    )


def _write_outputs(run: StateThresholdExperimentRun, *, strict_variant: bool = False) -> None:
    run.processed_dir.mkdir(parents=True)
    run.research_dir.mkdir(parents=True)
    run.ohlc_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "Date": ["2026-01-01 00:00:00", "2026-01-01 04:00:00"],
            "Open": [1.0, 1.1],
            "High": [1.2, 1.3],
            "Low": [0.9, 1.0],
            "Close": [1.1, 1.2],
            "Volume": [0, 0],
        }
    ).to_csv(run.ohlc_path, index=False)
    pd.DataFrame(
        {
            "Structure_ID": ["STR_1", "STR_2", "STR_3"],
            "Duration_Seconds": [100, 200, 300],
            "Structural_Confidence": [0.7, 0.8, 0.9],
        }
    ).to_csv(run.processed_dir / "structures.csv", index=False)
    states = ["DIRECTIONAL_DISPLACEMENT", "DIRECTIONAL_EXPANSION", "COMPLEX_CONSOLIDATION"]
    if strict_variant:
        states = ["UNCLASSIFIED", "DIRECTIONAL_EXPANSION", "COMPLEX_CONSOLIDATION"]
    pd.DataFrame(
        {
            "Market_State": states,
            "State_Confidence": [0.7, 0.8, 0.9],
        }
    ).to_csv(run.processed_dir / "market_states.csv", index=False)
    pd.DataFrame(
        {
            "Transition_Label": ["A_TO_B", "B_TO_C"],
            "State_Changed": [True, "False"],
            "Direction_Changed": ["yes", "no"],
            "Transition_Stability": [0.4, 0.6],
        }
    ).to_csv(run.processed_dir / "state_transitions.csv", index=False)
    pd.DataFrame(
        {
            "condition_id": ["COND_1", "COND_2", "COND_3"],
            "low_sample_size": ["True", "False", "yes"],
        }
    ).to_csv(run.research_dir / "condition_summaries.csv", index=False)
    pd.DataFrame({"Outcome_ID": ["OUT_1", "OUT_2"]}).to_csv(run.research_dir / "price_outcomes.csv", index=False)
    pd.DataFrame(
        {
            "Condition_ID": ["COND_1", "COND_2"],
            "Low_Sample_Size": [True, False],
            "Average_Forward_Range_Pips": [10.0, 14.0],
            "Average_Outcome_Magnitude_Pips": [5.0, 7.0],
            "Direction_Alignment_Rate": [0.4, 0.6],
            "Average_Forward_Close_Return_Pips": [1.0, 3.0],
        }
    ).to_csv(run.research_dir / "condition_price_outcome_summary.csv", index=False)


def test_collect_state_threshold_metrics_reads_outputs_case_insensitively(tmp_path) -> None:
    run = _run(tmp_path)
    _write_outputs(run)

    row = collect_state_threshold_metrics(run, _result(run))

    assert row.ohlc_rows == 2
    assert row.structures_detected == 3
    assert row.average_structure_duration == 200
    assert row.states_generated == 3
    assert row.directional_state_ratio == 2 / 3
    assert row.compression_consolidation_ratio == 1 / 3
    assert row.conditions_evaluated == 3
    assert row.condition_summary_rows == 3
    assert row.low_sample_conditions_research == 2
    assert row.price_outcomes_generated == 2
    assert row.low_sample_conditions_price_outcome == 1
    assert row.average_forward_range_pips == 12.0


def test_apply_baseline_comparisons_adds_relative_metrics(tmp_path) -> None:
    baseline = _run(tmp_path, "state_baseline")
    strict = _run(tmp_path, "directional_stricter")
    _write_outputs(baseline)
    _write_outputs(strict, strict_variant=True)
    baseline_row = collect_state_threshold_metrics(baseline, _result(baseline))
    strict_row = collect_state_threshold_metrics(strict, _result(strict))

    rows = apply_baseline_comparisons([baseline_row, strict_row])
    compared = next(row for row in rows if row.profile_id == "directional_stricter")

    assert compared.relative_directional_state_ratio_vs_baseline == -0.5
    assert "Baseline comparison" in compared.experiment_notes


def test_missing_optional_metric_columns_default_to_zero(tmp_path) -> None:
    run = _run(tmp_path)
    run.ohlc_path.parent.mkdir(parents=True)
    run.processed_dir.mkdir(parents=True)
    run.research_dir.mkdir(parents=True)
    pd.DataFrame({"Date": ["2026-01-01"], "Open": [1], "High": [1], "Low": [1], "Close": [1]}).to_csv(
        run.ohlc_path,
        index=False,
    )
    pd.DataFrame({"condition_type": ["A", "B"]}).to_csv(run.research_dir / "condition_summaries.csv", index=False)

    row = collect_state_threshold_metrics(run, _result(run))

    assert row.conditions_evaluated == 2
    assert row.low_sample_conditions_research == 0
