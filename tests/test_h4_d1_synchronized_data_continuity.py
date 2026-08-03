import pandas as pd

from sqre.h4_d1_synchronized_data_preparation.config import H4D1SynchronizedDataPreparationConfig
from sqre.h4_d1_synchronized_data_preparation.h4_continuity_validator import validate_h4_continuity
from sqre.h4_d1_synchronized_data_preparation.models import NormalizedOhlcResult


def _normalized(dates: list[str], valid: bool = True) -> NormalizedOhlcResult:
    frame = pd.DataFrame(
        {
            "Date": dates,
            "Open": [1.0] * len(dates),
            "High": [1.1] * len(dates),
            "Low": [0.9] * len(dates),
            "Close": [1.05] * len(dates),
            "Volume": [0] * len(dates),
            "Symbol": ["EURUSD"] * len(dates),
            "Timeframe": ["H4"] * len(dates),
            "Source_File": ["synthetic.csv"] * len(dates),
            "Normalization_Diagnostic": ["OK"] * len(dates),
        }
    )
    return NormalizedOhlcResult(frame, len(frame), len(frame), len(frame), 0, 0, "OK", valid)


def test_validate_h4_continuity_classifies_full_sequence():
    result = validate_h4_continuity(
        _normalized(["2026-07-01 00:00:00", "2026-07-01 04:00:00", "2026-07-01 08:00:00"]),
        H4D1SynchronizedDataPreparationConfig(),
    )

    assert result.h4_continuity_class == "FULL_H4_CONTINUITY"
    assert result.continuity_ratio == 1.0
    assert result.gap_count == 0


def test_validate_h4_continuity_counts_regular_gaps():
    result = validate_h4_continuity(
        _normalized(["2026-07-01 00:00:00", "2026-07-01 08:00:00"]),
        H4D1SynchronizedDataPreparationConfig(),
    )

    assert result.gap_count == 1
    assert result.estimated_missing_h4_candle_count == 1
    assert result.h4_continuity_class == "PARTIAL_H4_CONTINUITY"


def test_validate_h4_continuity_separates_weekend_gaps():
    result = validate_h4_continuity(
        _normalized(["2026-07-03 20:00:00", "2026-07-06 00:00:00"]),
        H4D1SynchronizedDataPreparationConfig(),
    )

    assert result.weekend_gap_count == 1
    assert result.gap_count == 1


def test_validate_h4_continuity_handles_empty_h4_input():
    result = validate_h4_continuity(_normalized([]), H4D1SynchronizedDataPreparationConfig())

    assert result.h4_continuity_class == "H4_INPUT_MISSING"
    assert result.continuity_ratio == 0.0
