from pathlib import Path

import pytest

from sqre.m15_duration_calibration_review.loader import load_m15_duration_experiment_summary


def test_loader_reads_synthetic_experiment_summary(tmp_path):
    path = _summary_path(tmp_path)

    rows = load_m15_duration_experiment_summary(path)

    assert len(rows) == 1
    assert rows[0].scenario_id == "eurusd_m15_period_1"
    assert rows[0].experiment_profile == "m15_duration_8h_baseline"
    assert rows[0].timeframe == "M15"


def test_loader_handles_case_insensitive_required_columns_and_ratio_aliases(tmp_path):
    path = tmp_path / "summary.csv"
    path.write_text(
        "\n".join(
            [
                "scenario_id,timeframe,experiment_id,status,max_structure_duration_seconds,structures_detected,"
                "average_structure_duration,unique_states,most_common_state,average_forward_range_pips,"
                "direction_alignment_rate,low_sample_conditions_research,low_sample_conditions_price_outcome,"
                "directional_ratio",
                "eurusd_m15_period_1,M15,m15_duration_4h,COMPLETED,14400,10,7200,5,DIRECTIONAL_DRIFT,8,0.4,10,9,0.25",
            ]
        ),
        encoding="utf-8",
    )

    rows = load_m15_duration_experiment_summary(path)

    assert rows[0].directional_state_ratio == 0.25
    assert rows[0].has_directional_count_columns is False


def test_loader_fills_missing_optional_count_columns_with_zero(tmp_path):
    rows = load_m15_duration_experiment_summary(_summary_path(tmp_path))

    assert rows[0].states_generated == 0
    assert rows[0].directional_displacement_count == 0
    assert rows[0].low_quality_structure_count == 0


def test_loader_fails_clearly_when_required_columns_are_missing(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("Scenario_ID,Timeframe\nx,M15\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required M15 duration review column"):
        load_m15_duration_experiment_summary(path)


def _summary_path(tmp_path: Path) -> Path:
    path = tmp_path / "summary.csv"
    path.write_text(
        "\n".join(
            [
                _header(),
                "eurusd_m15_period_1,M15,m15_duration_8h_baseline,COMPLETED,28800,12,25000,7,"
                "DIRECTIONAL_DRIFT,8,0.4,10,9",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _header() -> str:
    return (
        "Scenario_ID,Timeframe,Experiment_Profile,Status,Max_Structure_Duration_Seconds,"
        "Structures_Detected,Average_Structure_Duration,Unique_States,Most_Common_State,"
        "Average_Forward_Range_Pips,Direction_Alignment_Rate,Low_Sample_Conditions_Research,"
        "Low_Sample_Conditions_Price_Outcome"
    )
