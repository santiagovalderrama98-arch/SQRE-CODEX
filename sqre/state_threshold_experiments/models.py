"""Dataclass models for state threshold experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BaseStateThresholdScenario:
    scenario_id: str
    symbol: str
    timeframe: str
    ohlc_path: Path


@dataclass(frozen=True)
class StateThresholdExperimentConfig:
    experiment_name: str
    symbol: str
    pip_size: float
    forward_candles: list[int]
    minimum_sample_size: int
    baseline_max_structure_duration_seconds: dict[str, int]
    state_config_path: Path
    base_scenarios: list[BaseStateThresholdScenario]
    profiles: list[str]


@dataclass(frozen=True)
class StateThresholdExperimentRun:
    experiment_run_id: str
    profile_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    ohlc_path: Path
    state_config_path: Path
    max_structure_duration_seconds: int
    minimum_sample_size: int
    forward_candles: list[int]
    output_dir: Path
    processed_dir: Path
    research_dir: Path
    reports_dir: Path


@dataclass(frozen=True)
class StateThresholdExperimentRunResult:
    experiment_run_id: str
    profile_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    status: str
    message: str
    started_at: str
    completed_at: str
    output_dir: Path


@dataclass(frozen=True)
class StateThresholdExperimentMetricsRow:
    experiment_run_id: str
    profile_id: str
    scenario_id: str
    symbol: str
    timeframe: str
    status: str
    message: str
    period_start: str = ""
    period_end: str = ""
    ohlc_rows: int = 0
    structures_detected: int = 0
    average_structure_duration: float = 0.0
    average_structural_confidence: float = 0.0
    states_generated: int = 0
    unique_states: int = 0
    most_common_state: str = ""
    most_common_state_ratio: float = 0.0
    directional_displacement_count: int = 0
    directional_expansion_count: int = 0
    directional_drift_count: int = 0
    volatile_rotation_count: int = 0
    complex_consolidation_count: int = 0
    neutral_compression_count: int = 0
    low_quality_structure_count: int = 0
    unclassified_count: int = 0
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
    average_transition_stability: float = 0.0
    conditions_evaluated: int = 0
    condition_summary_rows: int = 0
    low_sample_conditions_research: int = 0
    research_low_sample_rate: float = 0.0
    price_outcomes_generated: int = 0
    price_outcome_summary_rows: int = 0
    low_sample_conditions_price_outcome: int = 0
    price_outcome_low_sample_rate: float = 0.0
    average_forward_range_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    average_forward_close_return_pips: float = 0.0
    relative_most_common_state_ratio_vs_baseline: float = 0.0
    relative_directional_state_ratio_vs_baseline: float = 0.0
    relative_state_diversity_change_vs_baseline: float = 0.0
    relative_volatile_rotation_ratio_vs_baseline: float = 0.0
    relative_compression_consolidation_ratio_vs_baseline: float = 0.0
    relative_unclassified_rate_vs_baseline: float = 0.0
    relative_low_quality_rate_vs_baseline: float = 0.0
    relative_forward_range_change_vs_baseline: float = 0.0
    absolute_most_common_state_ratio_change_vs_baseline: float = 0.0
    absolute_directional_state_ratio_change_vs_baseline: float = 0.0
    absolute_volatile_rotation_ratio_change_vs_baseline: float = 0.0
    absolute_compression_consolidation_ratio_change_vs_baseline: float = 0.0
    absolute_unclassified_rate_change_vs_baseline: float = 0.0
    absolute_low_quality_rate_change_vs_baseline: float = 0.0
    absolute_forward_range_change_vs_baseline: float = 0.0
    experiment_notes: str = ""


@dataclass(frozen=True)
class StateThresholdExperimentSummary:
    experiment_name: str
    runs_configured: int
    runs_completed: int
    runs_missing_input: int
    runs_failed: int
    summary_rows: int
    output_path: Path
    report_path: Path
