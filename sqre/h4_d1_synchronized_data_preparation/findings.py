"""Findings and readiness classification for synchronized H4/D1 data."""

from __future__ import annotations

from sqre.h4_d1_synchronized_data_preparation.models import H4D1SynchronizedDataSummary, SynchronizationReviewRow


def build_summary(synchronization: SynchronizationReviewRow) -> H4D1SynchronizedDataSummary:
    readiness = _readiness_flag(synchronization.synchronization_quality_class)
    return H4D1SynchronizedDataSummary(
        symbol=synchronization.symbol,
        h4_timeframe=synchronization.h4_timeframe,
        d1_timeframe=synchronization.d1_timeframe,
        h4_row_count=synchronization.h4_row_count,
        d1_row_count=synchronization.d1_row_count,
        aligned_h4_row_count=synchronization.aligned_h4_row_count,
        unaligned_h4_row_count=synchronization.unaligned_h4_row_count,
        full_d1_candle_count=synchronization.full_d1_candle_count,
        partial_d1_candle_count=synchronization.partial_d1_candle_count,
        low_coverage_d1_candle_count=synchronization.low_coverage_d1_candle_count,
        continuity_ratio=synchronization.continuity_ratio,
        synchronization_coverage_ratio=synchronization.synchronization_coverage_ratio,
        dominant_synchronization_quality_class=synchronization.synchronization_quality_class,
        h4_d1_synchronized_data_readiness_flag=readiness,
        h4_d1_synchronized_data_diagnostic=_diagnostic(readiness),
        recommended_follow_up=_follow_up(readiness),
    )


def readiness_assessment(summary: H4D1SynchronizedDataSummary | None) -> list[str]:
    if summary is None:
        return ["- Synchronized data summary was not produced."]
    return [
        f"- Dominant synchronization quality class: {summary.dominant_synchronization_quality_class}",
        f"- H4/D1 synchronized data readiness flag: {summary.h4_d1_synchronized_data_readiness_flag}",
        f"- Recommended follow-up: {summary.recommended_follow_up}",
        "- This review prepares OHLC data only and does not produce state or regime interpretation.",
    ]


def potential_follow_up_areas() -> list[str]:
    return [
        "H4 timestamped state/transition generation from synchronized H4 data",
        "D1 timestamped regime/state generation from synchronized D1 data",
        "H4/D1 same-time context alignment table",
        "Provider history coverage review",
        "Research reference-store design",
    ]


def do_not_change_yet_lines() -> list[str]:
    return [
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
        "No Decision Engine was added.",
        "No operational logic was added.",
        "No provider behavior was changed.",
        "No state generation was performed.",
        "No transition generation was performed.",
        "No D1 regime generation was performed.",
        "No same-time H4/D1 interpretation was produced.",
    ]


def limitation_lines() -> list[str]:
    return [
        "Findings depend on available local H4 data unless explicit download is enabled.",
        "D1 candles are derived from H4 and depend on H4 completeness.",
        "Timezone assumptions must be reviewed before final historical calibration.",
        "Data-level candle alignment is not equivalent to structural interpretation.",
        "No operational decision is produced.",
    ]


def _readiness_flag(quality: str) -> str:
    if quality == "READY_SYNCHRONIZED_H4_D1_DATA":
        return "READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION"
    if quality == "PARTIAL_SYNCHRONIZED_H4_D1_DATA":
        return "PARTIAL_READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION"
    if quality == "INPUT_MISSING":
        return "NOT_READY_H4_DATA_MISSING"
    if quality == "LOW_QUALITY_SYNCHRONIZED_H4_D1_DATA":
        return "NOT_READY_H4_DATA_QUALITY_REVIEW_REQUIRED"
    return "INPUT_COMPLETENESS_REVIEW_REQUIRED"


def _diagnostic(readiness: str) -> str:
    mapping = {
        "READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION": "Synchronized H4/D1 OHLC data is ready for later timestamped generation.",
        "PARTIAL_READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION": "Synchronized H4/D1 OHLC data is partially ready.",
        "NOT_READY_H4_DATA_QUALITY_REVIEW_REQUIRED": "H4 data quality requires review.",
        "NOT_READY_H4_DATA_MISSING": "H4 historical OHLC data is missing.",
        "INPUT_COMPLETENESS_REVIEW_REQUIRED": "Input completeness must be reviewed.",
    }
    return mapping.get(readiness, "Synchronized data readiness could not be classified.")


def _follow_up(readiness: str) -> str:
    if readiness in {
        "READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION",
        "PARTIAL_READY_FOR_TIMESTAMPED_H4_D1_STATE_REGIME_GENERATION",
    }:
        return "GENERATE_TIMESTAMPED_H4_D1_STATE_REGIME_TABLES"
    if readiness == "NOT_READY_H4_DATA_MISSING":
        return "PROVIDE_H4_HISTORICAL_OHLC"
    return "REVIEW_H4_SYNCHRONIZED_DATA_INPUTS"
