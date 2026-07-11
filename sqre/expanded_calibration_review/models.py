"""Dataclass models for expanded historical calibration review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ExpandedValidationScenarioSummary:
    scenario_id: str
    timeframe: str
    ohlc_rows: int = 0
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
    low_quality_structure_count: int = 0
    unclassified_count: int = 0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    low_sample_conditions_research: int = 0
    low_sample_conditions_price_outcome: int = 0
    source_file: str = ""


@dataclass(frozen=True)
class TimeframeCalibrationReviewRow:
    timeframe: str
    scenario_count: int
    scenario_ids: str
    average_ohlc_rows: float
    total_ohlc_rows: int
    average_structures_detected: float
    min_structures_detected: int
    max_structures_detected: int
    structure_count_range: int
    structure_count_cv: float
    average_structure_duration: float
    min_average_structure_duration: float
    max_average_structure_duration: float
    structure_duration_cv: float
    average_unique_states: float
    min_unique_states: int
    max_unique_states: int
    state_diversity_range: int
    most_common_state_mode: str
    directional_displacement_total: int
    directional_expansion_total: int
    volatile_rotation_total: int
    complex_consolidation_total: int
    low_quality_structure_total: int
    unclassified_total: int
    average_directional_state_ratio: float
    average_complex_consolidation_ratio: float
    average_volatile_rotation_ratio: float
    average_low_quality_rate: float
    average_unclassified_rate: float
    average_forward_range_pips: float
    min_forward_range_pips: float
    max_forward_range_pips: float
    forward_range_cv: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    min_direction_alignment_rate: float
    max_direction_alignment_rate: float
    average_low_sample_conditions_research: float
    average_low_sample_conditions_price_outcome: float
    max_low_sample_conditions_research: int
    max_low_sample_conditions_price_outcome: int
    structural_stability_flag: str
    state_diversity_flag: str
    low_sample_pressure_flag: str
    forward_range_regime_sensitivity_flag: str
    unclassified_pressure_flag: str
    low_quality_pressure_flag: str
    diagnostic_profile: str
    recommended_follow_up: str


@dataclass(frozen=True)
class ExpandedCalibrationFinding:
    timeframe: str
    finding_type: str
    flag: str
    message: str


@dataclass(frozen=True)
class ExpandedCalibrationReviewSummary:
    input_files: list[str] = field(default_factory=list)
    rows_loaded: int = 0
    timeframes_reviewed: int = 0
    summary_rows: int = 0
    output_path: Path = Path("data/validation/expanded_historical_calibration_review/expanded_calibration_review_summary.csv")
    report_path: Path = Path("data/validation/expanded_historical_calibration_review/expanded_calibration_review_report.txt")
