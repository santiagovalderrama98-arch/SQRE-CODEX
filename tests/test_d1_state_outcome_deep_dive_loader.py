from pathlib import Path

import pytest

from sqre.d1_state_outcome_deep_dive.loader import (
    load_regime_outcomes,
    load_regime_sensitive_profiles,
    load_research_ready_profiles,
)


def test_loader_reads_synthetic_research_ready_profiles_case_insensitive(tmp_path: Path):
    _write_ready_profiles(tmp_path)

    profiles = load_research_ready_profiles(tmp_path)

    assert len(profiles) == 2
    assert profiles[0].condition_type == "STATE_CONDITION"
    assert profiles[0].profile_type == "RESEARCH_READY"
    assert profiles[0].forward_window == 3


def test_loader_reads_synthetic_regime_condition_outcomes_case_insensitive(tmp_path: Path):
    _write_regime_outcomes(tmp_path)

    outcomes = load_regime_outcomes(tmp_path)

    assert len(outcomes) == 2
    assert outcomes[0].regime_id == "R1"
    assert outcomes[0].average_forward_range_pips == 10.0


def test_loader_handles_missing_optional_regime_sensitive_file(tmp_path: Path):
    assert load_regime_sensitive_profiles(tmp_path) == []


def test_loader_fails_when_required_profile_file_is_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_research_ready_profiles(tmp_path)


def _write_ready_profiles(root: Path) -> None:
    (root / "d1_research_ready_condition_profiles.csv").write_text(
        "\n".join(
            [
                "condition_type,condition_label,forward_window,regime_count,total_sample_size,"
                "average_forward_range_pips,average_outcome_magnitude_pips,average_direction_alignment_rate,"
                "forward_range_cv,outcome_magnitude_cv,condition_research_class",
                "STATE_CONDITION,DIRECTIONAL_EXPANSION,3,4,80,12,4,0.6,0.1,0.2,RESEARCH_READY_DESCRIPTIVE",
                "TRANSITION_CONDITION,A_TO_B,3,4,80,12,4,0.6,0.1,0.2,RESEARCH_READY_DESCRIPTIVE",
            ]
        ),
        encoding="utf-8",
    )


def _write_regime_outcomes(root: Path) -> None:
    (root / "d1_regime_condition_outcomes.csv").write_text(
        "\n".join(
            [
                "regime_id,regime_label,scenario_id,timeframe,condition_type,condition_label,forward_window,"
                "sample_size,average_forward_close_return_pips,average_forward_range_pips,"
                "average_outcome_magnitude_pips,direction_alignment_rate",
                "R1,Regime 1,S1,D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,30,1,10,4,0.5",
                "R2,Regime 2,S2,D1,STATE_CONDITION,DIRECTIONAL_EXPANSION,3,40,3,20,8,0.7",
            ]
        ),
        encoding="utf-8",
    )
