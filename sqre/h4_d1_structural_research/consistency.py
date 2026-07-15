"""Shared consistency metrics for H4/D1 structural research."""

from __future__ import annotations

import statistics


def mean(values: list[int | float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def cv(values: list[int | float]) -> float:
    if not values:
        return 0.0
    average = mean(values)
    if average == 0:
        return 0.0
    return float(statistics.pstdev(values) / average)


def ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def mode(values: list[str]) -> str:
    clean = [value for value in values if value]
    if not clean:
        return ""
    return max(sorted(set(clean)), key=clean.count)


def adequacy_flag(total: int, minimum_sample_size: int) -> str:
    return "ADEQUATE" if total >= minimum_sample_size else "LOW_SAMPLE"


def consistency_flag(coefficient: float, threshold: float) -> str:
    return "CONSISTENT" if coefficient <= threshold else "VARIABLE"


def sensitivity_flag(coefficient: float, threshold: float) -> str:
    return "HIGH" if coefficient >= threshold else "MODERATE"


def stability_flag(coefficient: float, threshold: float) -> str:
    return "STABLE" if coefficient <= threshold else "VARIABLE"
