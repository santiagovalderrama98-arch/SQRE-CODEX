from __future__ import annotations

from sqre.h4_d1_aligned_forward_outcome_research.h4_price_path_index import H4PricePathIndex
from sqre.h4_d1_aligned_forward_outcome_research.loader import load_h4_ohlc
from tests.h4_d1_aligned_forward_outcome_test_utils import write_forward_outcome_inputs


def test_price_path_index_finds_anchor_candle_by_timestamp(tmp_path):
    _, synchronized_dir, _ = write_forward_outcome_inputs(tmp_path)
    index = H4PricePathIndex(load_h4_ohlc(synchronized_dir))

    anchor = index.find_anchor("2026-01-01 04:00:00")

    assert anchor is not None
    assert anchor.index == 1
    assert anchor.close == 1.1000
