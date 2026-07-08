"""Dataclass models for SQRE calibration review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ValidationScenarioSummary:
    scenario_id: str
    status: str
    symbol: str
    timeframe: str
    period_start: str = ""
    period_end: str = ""
    ohlc_rows: int = 0
    max_structure_duration_seconds: int = 0
    forward_windows: str = ""
    structures_detected: int = 0
    average_structure_duration: float = 0.0
    states_generated: int = 0
    unique_states: int = 0
    most_common_state: str = ""
    directional_displacement_count: int = 0
    directional_expansion_count: int = 0
    directional_drift_count: int = 0
    volatile_rotation_count: int = 0
    complex_consolidation_count: int = 0
    neutral_compression_count: int = 0
    low_quality_structure_count: int = 0
    unclassified_count: int = 0
    average_state_confidence: float = 0.0
    transitions_generated: int = 0
    unique_transitions: int = 0
    state_change_rate: float = 0.0
    direction_change_rate: float = 0.0
    average_transition_magnitude: float = 0.0
    average_transition_stability: float = 0.0
    conditions_evaluated: int = 0
    low_sample_conditions_research: int = 0
    price_outcomes_generated: int = 0
    price_outcome_summary_rows: int = 0
    low_sample_conditions_price_outcome: int = 0
    average_forward_close_return_pips: float = 0.0
    median_forward_close_return_pips: float = 0.0
    average_forward_range_pips: float = 0.0
    average_favorable_displacement_pips: float = 0.0
    average_adverse_displacement_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    source_file: str = ""


@dataclass(frozen=True)
class CalibrationMetricsRow:
    scenario_id: str
    symbol: str
    timeframe: str
    status: str
    period_start: str
    period_end: str
    ohlc_rows: int
    duration_utilization_ratio: float
    most_common_state_ratio: float
    directional_state_ratio: float
    compression_consolidation_ratio: float
    volatile_rotation_ratio: float
    unclassified_rate: float
    low_quality_rate: float
    state_diversity: int
    transition_diversity: int
    state_change_rate: float
    direction_change_rate: float
    transition_stability: float
    research_low_sample_rate: float
    price_outcome_low_sample_rate: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    direction_alignment_rate: float
    average_forward_close_return_pips: float
    duration_near_max_flag: bool
    high_state_dominance_flag: bool
    low_state_diversity_flag: bool
    high_directional_ratio_flag: bool
    high_research_low_sample_flag: bool
    high_price_outcome_low_sample_flag: bool
    calibration_status: str
    calibration_notes: str = ""


@dataclass(frozen=True)
class CalibrationFinding:
    finding_id: str
    finding_type: str
    severity: str
    scope: str
    timeframe: str
    scenario_id: str
    metric_name: str
    metric_value: float
    threshold: float
    message: str


@dataclass(frozen=True)
class CalibrationReviewSummary:
    input_files: list[str] = field(default_factory=list)
    scenarios_loaded: int = 0
    completed_scenarios: int = 0
    missing_or_failed_scenarios: int = 0
    summary_rows: int = 0
    finding_count: int = 0
    review_status: str = "OK"
    output_path: Path = Path("data/validation/calibration_review_summary.csv")
    report_path: Path = Path("data/validation/calibration_review_report.txt")
