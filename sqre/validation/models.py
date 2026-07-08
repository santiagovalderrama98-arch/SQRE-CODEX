"""Dataclass models for SQRE validation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


COMPLETED = "COMPLETED"
MISSING_INPUT = "MISSING_INPUT"
FAILED = "FAILED"
SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class ValidationScenario:
    scenario_id: str
    symbol: str
    timeframe: str
    ohlc_path: Path
    max_structure_duration_seconds: int
    forward_candles: list[int]
    pip_size: float
    minimum_sample_size: int
    output_root: Path

    @property
    def scenario_output_dir(self) -> Path:
        return self.output_root / self.scenario_id

    @property
    def processed_dir(self) -> Path:
        return self.scenario_output_dir / "processed"

    @property
    def research_dir(self) -> Path:
        return self.scenario_output_dir / "research"

    @property
    def reports_dir(self) -> Path:
        return self.scenario_output_dir / "reports"


@dataclass(frozen=True)
class ValidationConfig:
    validation_name: str
    symbol: str
    pip_size: float
    minimum_sample_size: int
    scenarios: list[ValidationScenario]


@dataclass(frozen=True)
class ScenarioRunResult:
    scenario_id: str
    symbol: str
    timeframe: str
    status: str
    message: str
    ohlc_path: Path
    scenario_output_dir: Path
    processed_dir: Path
    research_dir: Path
    reports_dir: Path


@dataclass(frozen=True)
class ScenarioMetrics:
    scenario_id: str
    status: str
    message: str
    symbol: str
    timeframe: str
    ohlc_file: str
    period_start: str = ""
    period_end: str = ""
    ohlc_rows: int = 0
    max_structure_duration_seconds: int = 0
    forward_windows: str = ""
    structures_detected: int = 0
    average_structure_duration: float = 0.0
    average_price_displacement: float = 0.0
    most_common_direction: str = ""
    average_persistence_index: float = 0.0
    average_structural_complexity: float = 0.0
    average_structural_stability: float = 0.0
    average_structural_confidence: float = 0.0
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
    most_common_transition: str = ""
    most_common_sequence: str = ""
    state_change_rate: float = 0.0
    direction_change_rate: float = 0.0
    average_transition_magnitude: float = 0.0
    average_transition_stability: float = 0.0
    average_state_confidence_change: float = 0.0
    average_structural_quality_change: float = 0.0
    conditions_evaluated: int = 0
    forward_state_rows: int = 0
    forward_transition_rows: int = 0
    preceding_state_rows: int = 0
    sequence_outcome_rows: int = 0
    condition_summary_rows: int = 0
    low_sample_conditions_research: int = 0
    price_outcomes_generated: int = 0
    price_outcome_summary_rows: int = 0
    price_outcome_distribution_rows: int = 0
    low_sample_conditions_price_outcome: int = 0
    average_forward_close_return_pips: float = 0.0
    median_forward_close_return_pips: float = 0.0
    average_forward_range_pips: float = 0.0
    average_favorable_displacement_pips: float = 0.0
    average_adverse_displacement_pips: float = 0.0
    average_outcome_magnitude_pips: float = 0.0
    direction_alignment_rate: float = 0.0
    most_observed_condition: str = ""
    largest_average_forward_range_condition: str = ""
    highest_direction_alignment_condition: str = ""


@dataclass(frozen=True)
class ValidationSummary:
    validation_name: str
    scenarios_configured: int
    scenarios_selected: int
    scenarios_completed: int
    scenarios_missing_input: int
    scenarios_failed: int
    scenarios_skipped: int
    summary_csv_path: Path
    report_path: Path
