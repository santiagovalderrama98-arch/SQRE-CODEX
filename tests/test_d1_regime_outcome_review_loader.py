from pathlib import Path

import pytest

from sqre.d1_regime_outcome_review.loader import load_condition_profiles, optional_input_file_status


def test_load_condition_profiles_case_insensitive_columns(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "d1_regime_normalized_condition_profiles.csv").write_text(
        "\n".join(
            [
                "condition_type,condition_label,forward_window,regime_count,total_sample_size,"
                "average_forward_range_pips,average_outcome_magnitude_pips,average_direction_alignment_rate,"
                "forward_range_cv,outcome_magnitude_cv,regime_sensitivity_flag",
                "STATE,EXPANSION,20,4,80,22.5,8.0,0.61,0.12,0.18,STABLE",
            ]
        ),
        encoding="utf-8",
    )

    profiles = load_condition_profiles(input_dir)

    assert len(profiles) == 1
    assert profiles[0].condition_type == "STATE"
    assert profiles[0].total_sample_size == 80
    assert profiles[0].scenario_count == 0


def test_load_condition_profiles_fails_when_required_file_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_condition_profiles(tmp_path)


def test_optional_input_file_status_reports_presence(tmp_path: Path):
    (tmp_path / "d1_regime_scenario_inventory.csv").write_text("x\n", encoding="utf-8")

    status = optional_input_file_status(tmp_path)

    assert status["scenario_inventory"] is True
    assert status["condition_outcomes"] is False
