from pathlib import Path

import pytest

from sqre.m15_introduction_review.loader import load_context_from_master_summary, load_m15_validation_summary


def test_loader_accepts_case_insensitive_columns_and_ratio_aliases(tmp_path):
    path = tmp_path / "summary.csv"
    path.write_text(
        "\n".join(
            [
                "scenario_id,timeframe,status,ohlc_rows,structures_detected,average_structure_duration,"
                "unique_states,most_common_state,average_forward_range_pips,direction_alignment_rate,"
                "low_sample_conditions_research,low_sample_conditions_price_outcome,directional_ratio",
                "eurusd_m15_period_1,M15,COMPLETED,100,8,7200,5,DIRECTIONAL_DRIFT,9.5,0.42,2,3,0.25",
            ]
        ),
        encoding="utf-8",
    )

    rows = load_m15_validation_summary(path)

    assert len(rows) == 1
    assert rows[0].scenario_id == "eurusd_m15_period_1"
    assert rows[0].directional_state_ratio == 0.25
    assert rows[0].has_directional_count_columns is False


def test_loader_defaults_missing_optional_count_columns(tmp_path):
    path = _summary_path(tmp_path)

    rows = load_m15_validation_summary(path)

    assert rows[0].states_generated == 0
    assert rows[0].low_quality_structure_count == 0
    assert rows[0].average_outcome_magnitude_pips == 0.0


def test_loader_raises_for_missing_required_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("Scenario_ID,Timeframe\nx,M15\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required M15 review column"):
        load_m15_validation_summary(path)


def test_context_loader_uses_m5_and_h1_rows(tmp_path):
    path = tmp_path / "master.csv"
    path.write_text(
        "\n".join(
            [
                _header(),
                "m5_a,M5,COMPLETED,100,10,1000,4,DIRECTIONAL_DRIFT,5,0.4,6,1",
                "h1_a,H1,COMPLETED,100,20,1000,6,DIRECTIONAL_EXPANSION,5,0.4,8,1",
            ]
        ),
        encoding="utf-8",
    )

    context = load_context_from_master_summary(path)

    assert context.m5_average_structures == 10
    assert context.h1_average_structures == 20
    assert context.m5_average_unique_states == 4
    assert context.h1_low_sample == 8
    assert "M5 and H1" in context.interpretation


def test_context_loader_handles_missing_optional_path(tmp_path):
    context = load_context_from_master_summary(tmp_path / "missing.csv")

    assert context.m5_average_structures is None
    assert "not found" in context.interpretation


def _summary_path(tmp_path: Path) -> Path:
    path = tmp_path / "summary.csv"
    path.write_text(
        "\n".join(
            [
                _header(),
                "eurusd_m15_period_1,M15,COMPLETED,100,8,7200,5,DIRECTIONAL_DRIFT,9.5,0.42,2,3",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _header() -> str:
    return (
        "Scenario_ID,Timeframe,Status,OHLC_Rows,Structures_Detected,Average_Structure_Duration,"
        "Unique_States,Most_Common_State,Average_Forward_Range_Pips,Direction_Alignment_Rate,"
        "Low_Sample_Conditions_Research,Low_Sample_Conditions_Price_Outcome"
    )
