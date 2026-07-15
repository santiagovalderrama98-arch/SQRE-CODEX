import pandas as pd

from sqre.d1_regime_normalized_research.config import load_d1_regime_research_config
from sqre.d1_regime_normalized_research.loader import load_d1_regime_scenario_data


def test_loader_reads_summary_case_insensitively_and_finds_files(tmp_path):
    config = load_d1_regime_research_config("configs/validation/d1_regime_normalized_research.yaml")
    summary = tmp_path / "summary.csv"
    output_dir = tmp_path / "validation"
    scenario_dir = output_dir / "eurusd_d1_period_1" / "research"
    scenario_dir.mkdir(parents=True)
    pd.DataFrame({"Condition_Type": ["STATE_CONDITION"]}).to_csv(
        scenario_dir / "condition_price_outcome_summary.csv",
        index=False,
    )
    _summary_frame(lowercase=True).to_csv(summary, index=False)

    rows = load_d1_regime_scenario_data(summary, output_dir, config)

    assert len(rows) == 1
    assert rows[0].inventory.scenario_id == "eurusd_d1_period_1"
    assert rows[0].inventory.regime_id == "D1_REGIME_2021_2026"
    assert rows[0].inventory.price_outcome_summary_file_available is True
    assert rows[0].inventory.market_states_file_available is False


def test_loader_ignores_non_d1_rows(tmp_path):
    config = load_d1_regime_research_config("configs/validation/d1_regime_normalized_research.yaml")
    summary = tmp_path / "summary.csv"
    frame = _summary_frame(lowercase=False)
    frame.loc[1] = frame.loc[0]
    frame.loc[1, "Scenario_ID"] = "eurusd_h4_period_1"
    frame.loc[1, "Timeframe"] = "H4"
    frame.to_csv(summary, index=False)

    rows = load_d1_regime_scenario_data(summary, tmp_path / "validation", config)

    assert [row.inventory.scenario_id for row in rows] == ["eurusd_d1_period_1"]


def _summary_frame(lowercase: bool) -> pd.DataFrame:
    row = {
        "Scenario_ID": "eurusd_d1_period_1",
        "Timeframe": "D1",
        "Status": "COMPLETED",
        "OHLC_Rows": 100,
        "Structures_Detected": 10,
        "States_Generated": 20,
        "Unique_States": 3,
        "Most_Common_State": "DIRECTIONAL_DISPLACEMENT",
        "Average_Forward_Range_Pips": 30,
        "Direction_Alignment_Rate": 0.5,
        "Low_Sample_Conditions_Research": 1,
        "Low_Sample_Conditions_Price_Outcome": 2,
    }
    if lowercase:
        row = {key.lower(): value for key, value in row.items()}
    return pd.DataFrame([row])
