import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.models import H4ContinuityReviewRow
from sqre.h4_d1_synchronized_data_preparation.synchronization_review import build_synchronization_review


def _continuity(ratio: float = 1.0) -> H4ContinuityReviewRow:
    return H4ContinuityReviewRow(
        symbol="EURUSD",
        timeframe="H4",
        input_row_count=6,
        normalized_row_count=6,
        period_start="2026-07-01 00:00:00",
        period_end="2026-07-01 20:00:00",
        parsed_timestamp_count=6,
        duplicate_timestamp_count=0,
        conflicting_duplicate_timestamp_count=0,
        gap_count=0,
        large_gap_count=0,
        weekend_gap_count=0,
        estimated_missing_h4_candle_count=0,
        continuity_ratio=ratio,
        h4_continuity_class="FULL_H4_CONTINUITY",
        continuity_diagnostic="OK",
    )


def test_build_synchronization_review_classifies_ready_data():
    h4 = pd.DataFrame(index=range(6))
    d1 = pd.DataFrame({"D1_Candle_Quality_Class": ["FULL_H4_DERIVED_D1_CANDLE"]})
    alignment = pd.DataFrame({"H4_D1_Candle_Alignment_Class": ["H4_D1_CANDLE_ALIGNED"] * 6})

    review = build_synchronization_review(h4, d1, alignment, _continuity(), H4D1SynchronizedDataPreparationConfig())

    assert review.synchronization_quality_class == "READY_SYNCHRONIZED_H4_D1_DATA"
    assert review.synchronization_coverage_ratio == 1.0


def test_build_synchronization_review_classifies_missing_input():
    review = build_synchronization_review(
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        _continuity(0.0),
        H4D1SynchronizedDataPreparationConfig(),
    )

    assert review.synchronization_quality_class == "INPUT_MISSING"
    assert review.synchronization_coverage_ratio == 0.0
