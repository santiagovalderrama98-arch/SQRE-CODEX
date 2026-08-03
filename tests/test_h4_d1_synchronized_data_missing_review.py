from sqre.h4_d1_synchronized_data_preparation.missing_data_review import build_missing_data_review
from sqre.h4_d1_synchronized_data_preparation.models import H4ContinuityReviewRow, SynchronizationReviewRow


def _continuity(continuity_class: str = "FULL_H4_CONTINUITY") -> H4ContinuityReviewRow:
    return H4ContinuityReviewRow(
        symbol="EURUSD",
        timeframe="H4",
        input_row_count=0,
        normalized_row_count=0,
        period_start="",
        period_end="",
        parsed_timestamp_count=0,
        duplicate_timestamp_count=0,
        conflicting_duplicate_timestamp_count=0,
        gap_count=0,
        large_gap_count=0,
        weekend_gap_count=0,
        estimated_missing_h4_candle_count=0,
        continuity_ratio=0.0,
        h4_continuity_class=continuity_class,
        continuity_diagnostic="diagnostic",
    )


def _sync(unaligned: int = 0) -> SynchronizationReviewRow:
    return SynchronizationReviewRow(
        symbol="EURUSD",
        h4_timeframe="H4",
        d1_timeframe="D1",
        h4_row_count=0,
        d1_row_count=0,
        aligned_h4_row_count=0,
        unaligned_h4_row_count=unaligned,
        full_d1_candle_count=0,
        partial_d1_candle_count=0,
        low_coverage_d1_candle_count=0,
        continuity_ratio=0.0,
        synchronization_coverage_ratio=0.0,
        synchronization_quality_class="INPUT_MISSING",
        synchronization_diagnostic="diagnostic",
    )


def test_build_missing_data_review_requests_h4_ohlc_when_input_missing():
    rows = build_missing_data_review(_continuity("H4_INPUT_MISSING"), _sync())

    assert rows[0].missing_data_type == "H4_HISTORICAL_OHLC"
    assert rows[0].required_source_action == "PROVIDE_H4_HISTORICAL_OHLC"


def test_build_missing_data_review_reports_no_action_when_ready():
    rows = build_missing_data_review(_continuity(), _sync())

    assert rows[0].missing_data_type == "NONE"
    assert rows[0].required_source_action == "NO_ACTION_REQUIRED"
