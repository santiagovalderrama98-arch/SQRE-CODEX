"""Coverage review for timestamped H4/D1 generated outputs."""

from __future__ import annotations

from sqre.timestamped_h4_d1_state_regime_generation.config import TimestampedH4D1StateRegimeGenerationConfig
from sqre.timestamped_h4_d1_state_regime_generation.models import CoverageReviewRow


def build_coverage_review(
    *,
    h4_input_count: int,
    d1_input_count: int,
    h4_state_count: int,
    h4_transition_count: int,
    d1_state_count: int,
    config: TimestampedH4D1StateRegimeGenerationConfig,
) -> CoverageReviewRow:
    h4_state_class = _classify_output(h4_input_count, h4_state_count, config.minimum_state_count)
    h4_transition_class = _classify_output(h4_input_count, h4_transition_count, config.minimum_transition_count)
    d1_state_class = _classify_output(d1_input_count, d1_state_count, config.minimum_state_count)
    diagnostic = _diagnostic(h4_state_class, h4_transition_class, d1_state_class)
    return CoverageReviewRow(
        symbol=config.symbol,
        h4_timeframe=config.h4_timeframe,
        d1_timeframe=config.d1_timeframe,
        h4_input_row_count=h4_input_count,
        d1_input_row_count=d1_input_count,
        h4_state_row_count=h4_state_count,
        h4_transition_row_count=h4_transition_count,
        d1_state_row_count=d1_state_count,
        h4_state_coverage_class=h4_state_class,
        h4_transition_coverage_class=h4_transition_class,
        d1_state_coverage_class=d1_state_class,
        coverage_diagnostic=diagnostic,
    )


def _classify_output(input_count: int, output_count: int, minimum_count: int) -> str:
    if input_count == 0:
        return "INPUT_MISSING"
    if output_count >= minimum_count:
        return "TIMESTAMPED_OUTPUT_AVAILABLE"
    if output_count > 0:
        return "PARTIAL_TIMESTAMPED_OUTPUT_AVAILABLE"
    return "TIMESTAMPED_OUTPUT_MISSING"


def _diagnostic(h4_state_class: str, h4_transition_class: str, d1_state_class: str) -> str:
    classes = {h4_state_class, h4_transition_class, d1_state_class}
    if classes == {"TIMESTAMPED_OUTPUT_AVAILABLE"}:
        return "Timestamped H4 and D1 state/regime outputs are available for later alignment table generation."
    if "INPUT_MISSING" in classes:
        return "Synchronized input completeness requires review before timestamped output generation."
    if "TIMESTAMPED_OUTPUT_MISSING" in classes:
        return "One or more timestamped output tables are missing."
    return "Timestamped output coverage is partial and requires review."
