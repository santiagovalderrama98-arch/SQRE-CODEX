"""Local timeframe adapter for timestamped state/regime generation."""

from __future__ import annotations

import math

import pandas as pd

from sqre.market_states.classifier import MarketStateClassifier
from sqre.market_states.confidence import StateConfidenceCalculator
from sqre.market_states.models import StructuralInput


def build_timestamped_state_candidates(
    frame: pd.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    window_size: int,
    state_prefix: str,
) -> pd.DataFrame:
    """Build descriptive state rows from local OHLC windows.

    This uses existing SQRE market-state classification on derived structural
    inputs. It does not alter classifier behavior or production thresholds.
    """

    if frame.empty or len(frame) < max(window_size, 2):
        return pd.DataFrame()
    classifier = MarketStateClassifier()
    confidence = StateConfidenceCalculator()
    rows: list[dict[str, object]] = []
    for index, start in enumerate(range(0, len(frame), window_size), start=1):
        group = frame.iloc[start : start + window_size].copy()
        if len(group) < 2:
            continue
        structure = _window_to_structure(group, symbol=symbol, timeframe=timeframe, index=index)
        classification = classifier.classify(structure)
        state_confidence = confidence.calculate(structure, classification)
        rows.append(
            {
                "State_ID": f"{state_prefix}_{index:06d}",
                "Symbol": symbol,
                "Timeframe": timeframe,
                "State_Event_Time": structure.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "State_Event_Date": structure.end_time.date().isoformat(),
                "State_Start_Time": structure.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "State_End_Time": structure.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Market_State": classification.market_state,
                "Structure_ID": structure.structure_id,
                "Structure_Direction": structure.direction,
                "Structural_Efficiency": round(structure.structural_efficiency, 4),
                "Structural_Confidence": round(structure.structural_confidence, 4),
                "State_Confidence": round(state_confidence, 4),
                "State_Row_Source": "SYNCHRONIZED_OHLC_WINDOW_ADAPTER",
                "State_Diagnostic": "Timestamped state row derived from synchronized OHLC window.",
            }
        )
    return pd.DataFrame(rows)


def _window_to_structure(group: pd.DataFrame, *, symbol: str, timeframe: str, index: int) -> StructuralInput:
    start_time = pd.to_datetime(group["Date"].iloc[0]).to_pydatetime()
    end_time = pd.to_datetime(group["Date"].iloc[-1]).to_pydatetime()
    start_price = float(group["Open"].iloc[0])
    end_price = float(group["Close"].iloc[-1])
    high = float(group["High"].max())
    low = float(group["Low"].min())
    gross_range = max(high - low, 0.0)
    net_displacement = end_price - start_price
    direction = _direction(net_displacement, gross_range)
    candle_ranges = (pd.to_numeric(group["High"]) - pd.to_numeric(group["Low"])).abs()
    close_changes = pd.to_numeric(group["Close"]).diff().dropna()
    structural_efficiency = _ratio(abs(net_displacement), gross_range)
    persistence_index = _directional_persistence(close_changes)
    volatility = _bounded(float(candle_ranges.std() / candle_ranges.mean())) if float(candle_ranges.mean()) else 0.0
    complexity = _bounded(float(close_changes.diff().abs().mean() / candle_ranges.mean())) if len(close_changes) > 1 and float(candle_ranges.mean()) else 0.0
    stability = _bounded(1 - volatility)
    symmetry = _bounded(1 - abs(0.5 - persistence_index) * 2)
    confidence = _bounded((structural_efficiency + stability + max(persistence_index, symmetry)) / 3)
    duration = (end_time - start_time).total_seconds()
    return StructuralInput(
        structure_id=f"{timeframe}_SYNC_STR_{index:06d}",
        symbol=symbol,
        timeframe=timeframe,
        start_time=start_time,
        end_time=end_time,
        direction=direction,
        lifecycle_stage="TERMINATED",
        persistence_index=persistence_index,
        structural_complexity=complexity,
        structural_stability=stability,
        structural_efficiency=structural_efficiency,
        event_density=_bounded(len(group) / max(duration / 3600, 1)),
        structural_volatility=volatility,
        structural_symmetry=symmetry,
        structural_confidence=confidence,
        duration_seconds=duration,
        price_displacement=net_displacement,
        event_count=len(group),
        leg_count=max(len(group) - 1, 1),
    )


def _direction(net_displacement: float, gross_range: float) -> str:
    if gross_range == 0 or abs(net_displacement) / gross_range < 0.10:
        return "NEUTRAL"
    return "UP" if net_displacement > 0 else "DOWN"


def _directional_persistence(changes: pd.Series) -> float:
    if changes.empty:
        return 0.0
    positive = int((changes > 0).sum())
    negative = int((changes < 0).sum())
    dominant = max(positive, negative)
    return _bounded(dominant / len(changes))


def _ratio(numerator: float, denominator: float) -> float:
    if denominator == 0 or math.isnan(denominator):
        return 0.0
    return _bounded(numerator / denominator)


def _bounded(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(float(value), 1.0))
