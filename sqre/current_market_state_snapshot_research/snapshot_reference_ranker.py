"""Rank snapshot reference candidates."""

from __future__ import annotations

import pandas as pd

from sqre.research_query_interface_design.query_result_ranker import rank_reference_candidates


def rank_snapshot_reference_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    return rank_reference_candidates(candidates)
