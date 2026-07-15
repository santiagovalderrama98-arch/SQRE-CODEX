"""Models for H4/D1 structural research."""

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
class ScenarioInventoryRow:
    scenario_id: str
    timeframe: str
    status: str
    ohlc_rows: int
    structures_detected: int
    states_generated: int
    unique_states: int
    most_common_state: str
    average_forward_range_pips: float
    direction_alignment_rate: float
    low_sample_conditions_research: int
    low_sample_conditions_price_outcome: int
    market_states_file_available: bool = False
    transitions_file_available: bool = False
    condition_summaries_file_available: bool = False
    price_outcomes_file_available: bool = False
    price_outcome_summary_file_available: bool = False
    sequence_outcomes_file_available: bool = False


@dataclass(frozen=True)
class ScenarioData:
    inventory: ScenarioInventoryRow
    scenario_dir: Path
    market_states_path: Path | None = None
    transitions_path: Path | None = None
    condition_summaries_path: Path | None = None
    forward_state_distributions_path: Path | None = None
    forward_transition_distributions_path: Path | None = None
    sequence_outcomes_path: Path | None = None
    price_outcomes_path: Path | None = None
    price_outcome_summary_path: Path | None = None


@dataclass(frozen=True)
class StateResearchProfile:
    timeframe: str
    market_state: str
    scenario_count: int
    scenarios_present: str
    total_state_count: int
    average_state_count_per_scenario: float
    state_frequency_ratio: float
    average_state_confidence: float
    scenario_count_cv: float
    state_sample_adequacy_flag: str
    state_scenario_consistency_flag: str
    state_profile_diagnostic: str


@dataclass(frozen=True)
class TransitionResearchProfile:
    timeframe: str
    from_state: str
    to_state: str
    transition_label: str
    scenario_count: int
    scenarios_present: str
    total_transition_count: int
    average_transition_count_per_scenario: float
    transition_frequency_ratio: float
    scenario_count_cv: float
    transition_sample_adequacy_flag: str
    transition_consistency_flag: str
    transition_profile_diagnostic: str


@dataclass(frozen=True)
class PriceOutcomeProfile:
    timeframe: str
    condition_type: str
    condition_label: str
    forward_window: int
    scenario_count: int
    scenarios_present: str
    total_sample_size: int
    average_sample_size_per_scenario: float
    average_forward_close_return_pips: float
    median_forward_close_return_pips: float
    average_forward_range_pips: float
    average_favorable_displacement_pips: float
    average_adverse_displacement_pips: float
    average_outcome_magnitude_pips: float
    average_direction_alignment_rate: float
    forward_range_cv: float
    outcome_magnitude_cv: float
    scenario_sensitivity_flag: str
    sample_adequacy_flag: str
    outcome_profile_diagnostic: str


@dataclass(frozen=True)
class SequenceResearchProfile:
    timeframe: str
    sequence_label: str
    scenario_count: int
    scenarios_present: str
    total_sequence_count: int
    average_sequence_count_per_scenario: float
    sequence_sample_adequacy_flag: str
    sequence_profile_diagnostic: str


@dataclass(frozen=True)
class TimeframeResearchSummary:
    timeframe: str
    scenario_count: int
    completed_scenario_count: int
    total_ohlc_rows: int
    average_structures_detected: float
    structure_count_cv: float
    average_states_generated: float
    average_unique_states: float
    most_common_state_mode: str
    average_forward_range_pips: float
    forward_range_cv: float
    average_direction_alignment_rate: float
    average_low_sample_conditions_research: float
    average_low_sample_conditions_price_outcome: float
    state_profile_count: int
    transition_profile_count: int
    price_outcome_profile_count: int
    sequence_profile_count: int
    structural_maturity_flag: str
    research_sample_quality_flag: str
    scenario_sensitivity_flag: str
    timeframe_research_diagnostic: str
    recommended_follow_up: str


@dataclass(frozen=True)
class H4D1ResearchFinding:
    timeframe: str
    finding_type: str
    flag: str
    message: str


@dataclass(frozen=True)
class H4D1StructuralResearchResult:
    input_validation_summary: str
    validation_output_dir: str
    scenarios_loaded: int
    output_dir: Path
    report_path: Path
    inventory_rows: list[ScenarioInventoryRow] = field(default_factory=list)
    state_profiles: list[StateResearchProfile] = field(default_factory=list)
    transition_profiles: list[TransitionResearchProfile] = field(default_factory=list)
    price_outcome_profiles: list[PriceOutcomeProfile] = field(default_factory=list)
    sequence_profiles: list[SequenceResearchProfile] = field(default_factory=list)
    timeframe_summaries: list[TimeframeResearchSummary] = field(default_factory=list)
    findings: list[H4D1ResearchFinding] = field(default_factory=list)
