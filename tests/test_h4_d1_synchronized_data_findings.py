from sqre.h4_d1_synchronized_data_preparation.findings import build_summary
from sqre.h4_d1_synchronized_data_preparation.models import SynchronizationReviewRow


def _sync(quality: str) -> SynchronizationReviewRow:
    return SynchronizationReviewRow(
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
        h4_row_count=6,
        d1_row_count=1,
        aligned_h4_row_count=6,
        unaligned_h4_row_count=0,
        full_d1_candle_count=1,
        partial_d1_candle_count=0,
        low_coverage_d1_candle_count=0,
        continuity_ratio=1.0,
        synchronization_coverage_ratio=1.0,
        synchronization_quality_class=quality,
        synchronization_diagnostic="diagnostic",
    )


def test_build_summary_sets_ready_follow_up_for_ready_synchronized_data():
    summary = build_summary(_sync("READY_SYNCHRONIZED_H4_D1_DATA"))

    assert summary.h4_d1_synchronized_data_readiness_flag == "READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION"
    assert summary.recommended_follow_up == "GENERATE_TIMESTAMPED_H4_D1_STATE_REGIME_TABLES"


def test_build_summary_sets_missing_data_flag_for_missing_input():
    summary = build_summary(_sync("INPUT_MISSING"))

    assert summary.h4_d1_synchronized_data_readiness_flag == "NOT_READY_H4_DATA_MISSING"
    assert summary.recommended_follow_up == "PROVIDE_H4_HISTORICAL_OHLC"
