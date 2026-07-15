import pandas as pd
import pytest

from sqre.h4_d1_structural_research.loader import load_h4_d1_scenario_data


def test_loader_reads_summary_and_finds_scenario_files(tmp_path):
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    scenario_dir = output_dir / "eurusd_h4_period_1"
    (scenario_dir / "processed").mkdir(parents=True)
    (scenario_dir / "research").mkdir(parents=True)
    (scenario_dir / "processed" / "market_states.csv").write_text("Market_State\nA\n", encoding="utf-8")
    (scenario_dir / "processed" / "state_transitions.csv").write_text("Transition_Label\nA_TO_B\n", encoding="utf-8")
    (scenario_dir / "research" / "condition_summaries.csv").write_text("Condition_ID\nC1\n", encoding="utf-8")
    (scenario_dir / "research" / "price_outcomes.csv").write_text("Outcome_ID\nO1\n", encoding="utf-8")
    (scenario_dir / "research" / "condition_price_outcome_summary.csv").write_text(
        "Condition_Value\nA\n",
        encoding="utf-8",
    )
    (scenario_dir / "research" / "sequence_outcomes.csv").write_text("Sequence\nA -> B\n", encoding="utf-8")
    _write_summary(summary)

    rows = load_h4_d1_scenario_data(summary, output_dir)

    assert len(rows) == 1
    assert rows[0].inventory.scenario_id == "eurusd_h4_period_1"
    assert rows[0].inventory.market_states_file_available is True
    assert rows[0].inventory.transitions_file_available is True
    assert rows[0].inventory.condition_summaries_file_available is True
    assert rows[0].inventory.price_outcome_summary_file_available is True
    assert rows[0].inventory.sequence_outcomes_file_available is True


def test_loader_handles_case_insensitive_columns_and_missing_optional_files(tmp_path):
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    pd.DataFrame(
        [
            {
                "scenario_id": "eurusd_d1_period_1",
                "timeframe": "D1",
                "status": "COMPLETED",
                "ohlc_rows": 10,
                "structures_detected": 4,
                "states_generated": 4,
                "unique_states": 2,
                "most_common_state": "DIRECTIONAL_DRIFT",
                "average_forward_range_pips": 12,
                "direction_alignment_rate": 0.4,
                "low_sample_conditions_research": 1,
                "low_sample_conditions_price_outcome": 2,
            }
        ]
    ).to_csv(summary, index=False)

    rows = load_h4_d1_scenario_data(summary, output_dir)

    assert len(rows) == 1
    assert rows[0].inventory.timeframe == "D1"
    assert rows[0].inventory.market_states_file_available is False


def test_loader_fails_clearly_when_required_columns_are_missing(tmp_path):
    summary = tmp_path / "summary.csv"
    summary.write_text("Scenario_ID,Timeframe\nx,H4\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required H4/D1 research column"):
        load_h4_d1_scenario_data(summary, tmp_path / "validation")


def _write_summary(path):
    pd.DataFrame(
        [
            {
                "Scenario_ID": "eurusd_h4_period_1",
                "Timeframe": "H4",
                "Status": "COMPLETED",
                "OHLC_Rows": 10,
                "Structures_Detected": 4,
                "States_Generated": 4,
                "Unique_States": 2,
                "Most_Common_State": "DIRECTIONAL_DRIFT",
                "Average_Forward_Range_Pips": 12,
                "Direction_Alignment_Rate": 0.4,
                "Low_Sample_Conditions_Research": 1,
                "Low_Sample_Conditions_Price_Outcome": 2,
            }
        ]
    ).to_csv(path, index=False)
