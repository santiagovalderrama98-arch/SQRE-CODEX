"""Models for D1 regime-normalized research."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_SUMMARY_COLUMNS = [
    "Scenario_ID",
    "Timeframe",
    "Status",
    "OHLC_Rows",
    "Structures_Detected",
    "States_Generated",
    "Unique_States",
    "Most_Common_State",
    "Average_Forward_Range_Pips",
    "Direction_Alignment_Rate",
    "Low_Sample_Conditions_Research",
    "Low_Sample_Conditions_Price_Outcome",
]


@dataclass(frozen=True)
class D1RegimeScenarioInventoryRow:
    scenario_id: str
    timeframe: str
    status: str
    regime_id: str
    regime_label: str
    ohlc_rows: int
    structures_detected: int
    states_generated: int
    unique_states: int
    most_common_state: str
    average_forward_range_pips: float
    direction_alignment_rate: float
    low_sample_conditions_research: int
    low_sample_conditions_price_outcome: int
    price_outcome_summary_file_available: bool = False
    price_outcomes_file_available: bool = False
    market_states_file_available: bool = False
    transitions_file_available: bool = False


@dataclass(frozen=True)
class D1RegimeScenarioData:
    inventory: D1RegimeScenarioInventoryRow
    scenario_dir: Path
    price_outcome_summary_path: Path | None = None
    price_outcomes_path: Path | None = None
    market_states_path: Path | None = None
    transitions_path: Path | None = None


@dataclass(frozen=True)
class D1RegimeConditionOutcome:
    regime_id: str
    regime_label: str
    scenario_id: str
    timeframe: str
    condition_type: str
    condition_label: str
    forward_window: int
    sample_size: int
    average_forward_close_return_pips: float
    median_forward_close_return_pips: float
    average_forward_range_pips: float
    average_favorable_displacement_pips: float
    average_adverse_displacement_pips: float
    average_outcome_magnitude_pips: float
    direction_alignment_rate: float
    sample_adequacy_flag: str


@dataclass(frozen=True)
class D1RegimeConditionProfile:
    condition_type: str
    condition_label: str
    forward_window: int
    regime_count: int
    regimes_present: str
    scenario_count: int
    total_sample_size: int
    average_sample_size_per_regime: float
    average_forward_close_return_pips: float
    median_forward_close_return_pips_avg: float
    average_forward_range_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    forward_close_return_cv: float
    forward_range_cv: float
    outcome_magnitude_cv: float
    direction_alignment_cv: float
    min_forward_range_pips: float
    max_forward_range_pips: float
    range_dispersion_pips: float
    min_outcome_magnitude_pips: float
    max_outcome_magnitude_pips: float
    outcome_magnitude_dispersion_pips: float
    sample_adequacy_flag: str
    regime_coverage_flag: str
    regime_sensitivity_flag: str
    condition_profile_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class D1RegimeResearchSummary:
    timeframe: str
    scenario_count: int
    regime_count: int
    completed_scenario_count: int
    total_ohlc_rows: int
    average_structures_detected: float
    average_unique_states: float
    most_common_state_mode: str
    condition_profile_count: int
    state_condition_profile_count: int
    transition_condition_profile_count: int
    average_regime_count_per_profile: float
    adequate_profile_count: int
    low_sample_profile_count: int
    stable_outcome_profile_count: int
    moderate_sensitivity_profile_count: int
    high_sensitivity_profile_count: int
    average_forward_range_cv: float
    average_outcome_magnitude_cv: float
    average_direction_alignment_rate: float
    research_readiness_flag: str
    regime_sensitivity_profile: str
    recommended_follow_up: str


@dataclass(frozen=True)
class D1RegimeResearchResult:
    config_path: str
    input_validation_summary: str
    validation_output_dir: str
    output_dir: Path
    report_path: Path
    scenarios_loaded: int = 0
    regimes_loaded: int = 0
    inventory_rows: list[D1RegimeScenarioInventoryRow] = field(default_factory=list)
    condition_outcomes: list[D1RegimeConditionOutcome] = field(default_factory=list)
    condition_profiles: list[D1RegimeConditionProfile] = field(default_factory=list)
    state_profiles: list[D1RegimeConditionProfile] = field(default_factory=list)
    transition_profiles: list[D1RegimeConditionProfile] = field(default_factory=list)
    summary: D1RegimeResearchSummary | None = None
