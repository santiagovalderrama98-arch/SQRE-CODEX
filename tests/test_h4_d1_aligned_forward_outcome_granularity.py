from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.config import H4D1AlignedForwardOutcomeResearchConfig
from sqre.h4_d1_aligned_forward_outcome_research.forward_outcome_calculator import calculate_forward_outcomes
from sqre.h4_d1_aligned_forward_outcome_research.h4_price_path_index import H4PricePathIndex
from sqre.h4_d1_aligned_forward_outcome_research.loader import load_h4_ohlc, load_transition_alignment
from sqre.h4_d1_aligned_forward_outcome_research.outcome_profile_builder import build_outcome_profiles
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_outcome_profiles_include_all_context_granularities(tmp_path):
    alignment_dir, synchronized_dir, _ = write_forward_outcome_inputs(tmp_path)
    config = H4D1AlignedForwardOutcomeResearchConfig(
        forward_horizons=(1,),
        minimum_outcome_sample_size=1,
        minimum_context_outcome_sample_size=1,
    )
    outcomes = calculate_forward_outcomes(
        load_transition_alignment(alignment_dir),
        H4PricePathIndex(load_h4_ohlc(synchronized_dir)),
        config,
    )

    profiles = build_outcome_profiles(outcomes, config)

    assert set(profiles["Context_Granularity"]) == {
        "H4_TRANSITION_ONLY",
        "H4_TRANSITION_PLUS_D1_MARKET_STATE",
        "H4_TRANSITION_PLUS_D1_REGIME",
        "H4_TRANSITION_PLUS_D1_STATE_AND_REGIME",
    }
