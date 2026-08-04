from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.forward_outcome_calculator import calculate_forward_outcomes
from sqre.h4_d1_aligned_forward_outcome_research.h4_price_path_index import H4PricePathIndex
from sqre.h4_d1_aligned_forward_outcome_research.loader import load_h4_ohlc, load_transition_alignment
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_calculator_computes_close_change_and_excursions(tmp_path):
    alignment_dir, synchronized_dir, _ = write_forward_outcome_inputs(tmp_path)
    config = H4D1AlignedForwardOutcomeResearchConfig(forward_horizons=(1,))

    rows = calculate_forward_outcomes(
        load_transition_alignment(alignment_dir),
        H4PricePathIndex(load_h4_ohlc(synchronized_dir)),
        config,
    )

    first = rows.iloc[0]
    assert first["Forward_Close_Change_Pips"] == 10.0
    assert first["Forward_High_Excursion_Pips"] == 20.0
    assert first["Forward_Low_Excursion_Pips"] == -10.0
    assert first["Outcome_Completeness_Class"] == "COMPLETE_FORWARD_WINDOW"


def test_calculator_handles_incomplete_forward_windows(tmp_path):
    alignment_dir, synchronized_dir, _ = write_forward_outcome_inputs(tmp_path)
    config = H4D1AlignedForwardOutcomeResearchConfig(forward_horizons=(3,))

    rows = calculate_forward_outcomes(
        load_transition_alignment(alignment_dir),
        H4PricePathIndex(load_h4_ohlc(synchronized_dir)),
        config,
    )

    second = rows.iloc[1]
    assert second["Outcome_Completeness_Class"] == "PARTIAL_FORWARD_WINDOW"
    assert second["Directional_Follow_Through_Class"] == "FORWARD_DOWN_MOVE"
