from pathlib import Path

import pandas as pd

from sqre.validation.metrics import collect_scenario_metrics, metrics_to_frame
from sqre.validation.models import COMPLETED, ScenarioRunResult, ValidationScenario


def test_collect_scenario_metrics_from_generated_csvs(tmp_path):
    scenario = _scenario(tmp_path)
    scenario.processed_dir.mkdir(parents=True)
    scenario.research_dir.mkdir(parents=True)
    _write_csv(
        scenario.ohlc_path,
        [
            {"Date": "2026-01-01 00:00:00", "Open": 1.1, "High": 1.2, "Low": 1.0, "Close": 1.15, "Volume": 0},
            {"Date": "2026-01-01 00:05:00", "Open": 1.15, "High": 1.25, "Low": 1.1, "Close": 1.2, "Volume": 0},
        ],
    )
    _write_csv(
        scenario.processed_dir / "structures.csv",
        [
            {
                "Duration_Seconds": 300,
                "Price_Displacement": 0.001,
                "Direction": "UP",
                "Persistence_Index": 0.5,
                "Structural_Complexity": 0.2,
                "Structural_Stability": 0.8,
                "Structural_Confidence": 0.7,
            }
        ],
    )
    _write_csv(
        scenario.processed_dir / "market_states.csv",
        [
            {"Market_State": "DIRECTIONAL_EXPANSION", "State_Confidence": 0.8},
            {"Market_State": "DIRECTIONAL_EXPANSION", "State_Confidence": 0.6},
        ],
    )
    _write_csv(
        scenario.processed_dir / "state_transitions.csv",
        [
            {
                "Transition_Label": "A_TO_B",
                "State_Changed": True,
                "Direction_Changed": False,
                "Transition_Magnitude": 0.3,
                "Transition_Stability": 0.7,
                "State_Confidence_Change": 0.1,
                "Structural_Quality_Change": 0.2,
            }
        ],
    )
    _write_csv(scenario.processed_dir / "transition_sequences.csv", [{"Sequence": "A -> B"}])
    _write_csv(scenario.research_dir / "condition_summaries.csv", [{"Condition_ID": "C1", "Low_Sample_Size": True}])
    _write_csv(scenario.research_dir / "forward_state_distributions.csv", [{"Condition_ID": "C1"}])
    _write_csv(scenario.research_dir / "forward_transition_distributions.csv", [{"Condition_ID": "C1"}])
    _write_csv(scenario.research_dir / "preceding_state_distributions.csv", [{"Condition_ID": "C1"}])
    _write_csv(scenario.research_dir / "sequence_outcomes.csv", [{"Condition_ID": "C1"}])
    _write_csv(scenario.research_dir / "price_outcomes.csv", [{"Outcome_ID": "O1"}])
    _write_csv(
        scenario.research_dir / "condition_price_outcome_summary.csv",
        [
            {
                "Condition_Value": "DIRECTIONAL_EXPANSION",
                "Sample_Size": 7,
                "Low_Sample_Size": False,
                "Average_Forward_Close_Return_Pips": 1.5,
                "Median_Forward_Close_Return_Pips": 1.2,
                "Average_Forward_Range_Pips": 5.0,
                "Average_Max_Favorable_Displacement_Pips": 3.0,
                "Average_Max_Adverse_Displacement_Pips": -2.0,
                "Average_Outcome_Magnitude_Pips": 4.0,
                "Direction_Alignment_Rate": 0.75,
            }
        ],
    )
    _write_csv(scenario.research_dir / "price_outcome_distributions.csv", [{"Condition_ID": "C1"}])

    result = ScenarioRunResult(
        scenario_id=scenario.scenario_id,
        symbol=scenario.symbol,
        timeframe=scenario.timeframe,
        status=COMPLETED,
        message="Scenario completed",
        ohlc_path=scenario.ohlc_path,
        scenario_output_dir=scenario.scenario_output_dir,
        processed_dir=scenario.processed_dir,
        research_dir=scenario.research_dir,
        reports_dir=scenario.reports_dir,
    )
    metrics = collect_scenario_metrics(scenario, result)

    assert metrics.ohlc_rows == 2
    assert metrics.structures_detected == 1
    assert metrics.states_generated == 2
    assert metrics.directional_expansion_count == 2
    assert metrics.transitions_generated == 1
    assert metrics.price_outcomes_generated == 1
    assert metrics.direction_alignment_rate == 0.75
    assert metrics_to_frame([metrics]).iloc[0]["Scenario_ID"] == "eurusd_m5"


def _scenario(tmp_path: Path) -> ValidationScenario:
    return ValidationScenario(
        scenario_id="eurusd_m5",
        symbol="EURUSD",
        timeframe="M5",
        ohlc_path=tmp_path / "EURUSD_M5.csv",
        max_structure_duration_seconds=14400,
        forward_candles=[3, 6, 12],
        pip_size=0.0001,
        minimum_sample_size=5,
        output_root=tmp_path / "validation",
    )


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
