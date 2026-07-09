"""Dataclass models for SQRE calibration experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BaseExperimentScenario:
    scenario_id: str
    symbol: str
    timeframe: str
    ohlc_path: Path


@dataclass(frozen=True)
class DurationExperiment:
    experiment_id: str
    description: str
    max_structure_duration_seconds_by_timeframe: dict[str, int]


@dataclass(frozen=True)
class SampleSizeExperiment:
    experiment_id: str
    description: str
    minimum_sample_size: int


@dataclass(frozen=True)
class CalibrationExperimentConfig:
    experiment_name: str
    symbol: str
    pip_size: float
    forward_candles: list[int]
    base_scenarios: list[BaseExperimentScenario]
    duration_experiments: list[DurationExperiment]
    sample_size_experiments: list[SampleSizeExperiment]


@dataclass(frozen=True)
class ExperimentRun:
    experiment_run_id: str
    experiment_type: str
    experiment_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    ohlc_path: Path
    max_structure_duration_seconds: int
    minimum_sample_size: int
    forward_candles: list[int]
    output_dir: Path
    processed_dir: Path
    research_dir: Path
    reports_dir: Path


@dataclass(frozen=True)
class ExperimentRunResult:
    experiment_run_id: str
    experiment_type: str
    experiment_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    status: str
    message: str
    started_at: str
    completed_at: str
    output_dir: Path


@dataclass(frozen=True)
class ExperimentMetricsRow:
    experiment_run_id: str
    experiment_type: str
    experiment_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    status: str
    message: str
    period_start: str = ""
    period_end: str = ""
    ohlc_rows: int = 0
    max_structure_duration_seconds: int = 0
    minimum_sample_size: int = 0
    forward_windows: str = ""
    structures_detected: int = 0
    average_structure_duration: float = 0.0
    duration_utilization_ratio: float = 0.0
    average_price_displacement: float = 0.0
    most_common_direction: str = ""
    average_persistence_index: float = 0.0
    average_structural_complexity: float = 0.0
    average_structural_stability: float = 0.0
    average_structural_confidence: float = 0.0
    states_generated: int = 0
    unique_states: int = 0
    most_common_state: str = ""
    most_common_state_ratio: float = 0.0
    directional_state_ratio: float = 0.0
    compression_consolidation_ratio: float = 0.0
    volatile_rotation_ratio: float = 0.0
    unclassified_rate: float = 0.0
    low_quality_rate: float = 0.0
    average_state_confidence: float = 0.0
    transitions_generated: int = 0
    unique_transitions: int = 0
    most_common_transition: str = ""
    state_change_rate: float = 0.0
    direction_change_rate: float = 0.0
    average_transition_magnitude: float = 0.0
    average_transition_stability: float = 0.0
    conditions_evaluated: int = 0
    condition_summary_rows: int = 0
    low_sample_conditions_research: int = 0
    research_low_sample_rate: float = 0.0
    price_outcomes_generated: int = 0
    price_outcome_summary_rows: int = 0
    price_outcome_distribution_rows: int = 0
    low_sample_conditions_price_outcome: int = 0
    price_outcome_low_sample_rate: float = 0.0
    average_forward_close_return_pips: float = 0.0
    median_forward_close_return_pips: float = 0.0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    relative_structure_count_change_vs_baseline: float = 0.0
    relative_duration_change_vs_baseline: float = 0.0
    relative_state_diversity_change_vs_baseline: float = 0.0
    relative_forward_range_change_vs_baseline: float = 0.0
    experiment_notes: str = ""


@dataclass(frozen=True)
class CalibrationExperimentSummary:
    experiment_name: str
    runs_configured: int
    runs_completed: int
    runs_missing_input: int
    runs_failed: int
    summary_rows: int
    output_path: Path
    report_path: Path
