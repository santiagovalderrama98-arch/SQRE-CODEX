"""Regime sensitivity metrics."""

from __future__ import annotations

import statistics

from sqre.d1_regime_normalized_research.config import D1RegimeResearchConfig


def mean(values: list[float]) -> float:
    clean = [float(value) for value in values]
    return sum(clean) / len(clean) if clean else 0.0


def cv(values: list[float]) -> float:
    clean = [float(value) for value in values]
    avg = mean(clean)
    if len(clean) < 2 or avg == 0:
        return 0.0
    return statistics.pstdev(clean) / abs(avg)


def sample_adequacy_flag(total_sample_size: int, config: D1RegimeResearchConfig) -> str:
    return "ADEQUATE" if total_sample_size >= config.minimum_sample_size else "LOW_SAMPLE"


def regime_coverage_flag(regime_count: int, config: D1RegimeResearchConfig) -> str:
    return "SUFFICIENT" if regime_count >= config.minimum_regime_count else "LIMITED"


def regime_sensitivity_flag(forward_range_cv: float, outcome_magnitude_cv: float, config: D1RegimeResearchConfig) -> str:
    if (
        forward_range_cv >= config.high_regime_sensitivity_threshold
        or outcome_magnitude_cv >= config.high_regime_sensitivity_threshold
    ):
        return "HIGH"
    if (
        forward_range_cv >= config.moderate_regime_sensitivity_threshold
        or outcome_magnitude_cv >= config.moderate_regime_sensitivity_threshold
    ):
        return "MODERATE"
    return "STABLE"


def profile_diagnostic(sample_flag: str, coverage_flag: str, sensitivity_flag: str) -> str:
    if sample_flag == "LOW_SAMPLE":
        return "Condition outcome profile requires sample adequacy review"
    if coverage_flag == "LIMITED":
        return "Condition outcome profile has limited regime coverage"
    if sensitivity_flag == "HIGH":
        return "Condition outcome profile shows elevated regime sensitivity"
    if sensitivity_flag == "MODERATE":
        return "Condition outcome profile shows moderate regime sensitivity"
    return "Condition outcome profile appears stable across available D1 regimes"
