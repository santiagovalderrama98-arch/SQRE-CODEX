"""Scenario inventory loading for H4 timestamped context table generation."""

from __future__ import annotations

from collections import Counter

from sqre.h4_timestamped_context_table_generation.config import H4TimestampedContextTableGenerationConfig
from sqre.h4_timestamped_context_table_generation.loader import read_optional_csv, row_int, row_text
from sqre.h4_timestamped_context_table_generation.models import ScenarioInventoryRow, TimestampedContextRow


SCENARIO_ID_ALIASES = ["Scenario_ID", "Validation_Scenario_ID", "Sample_ID", "Period_ID"]
SYMBOL_ALIASES = ["Symbol", "symbol"]
TIMEFRAME_ALIASES = ["Timeframe", "timeframe"]
PERIOD_START_ALIASES = ["Period_Start", "Scenario_Start", "Start_Date", "From_Date"]
PERIOD_END_ALIASES = ["Period_End", "Scenario_End", "End_Date", "To_Date"]
OHLC_FILE_ALIASES = ["OHLC_File", "Ohlc_File", "Input_File", "Raw_File"]
STATUS_ALIASES = ["Scenario_Status", "Status", "Validation_Status"]
STATES_GENERATED_ALIASES = ["States_Generated", "State_Count", "Market_State_Count"]
TRANSITIONS_GENERATED_ALIASES = ["Transitions_Generated", "Transition_Count", "State_Transition_Count"]


def load_base_scenario_inventory(config: H4TimestampedContextTableGenerationConfig) -> list[ScenarioInventoryRow]:
    frame = read_optional_csv(config.h4_d1_validation_dir / "h4_d1_validation_summary.csv")
    if frame.empty:
        fallback = read_optional_csv(config.h4_d1_structural_research_dir / "h4_d1_scenario_inventory.csv")
        frame = fallback
    rows: list[ScenarioInventoryRow] = []
    for index, row in frame.iterrows():
        scenario_id = row_text(row, SCENARIO_ID_ALIASES, f"SCENARIO_{index + 1:06d}")
        timeframe = row_text(row, TIMEFRAME_ALIASES, config.timeframe)
        if timeframe and timeframe.upper() != config.timeframe.upper():
            continue
        rows.append(
            ScenarioInventoryRow(
                scenario_id=scenario_id,
                symbol=row_text(row, SYMBOL_ALIASES, config.symbol) or config.symbol,
                timeframe=timeframe or config.timeframe,
                period_start=row_text(row, PERIOD_START_ALIASES),
                period_end=row_text(row, PERIOD_END_ALIASES),
                ohlc_file=row_text(row, OHLC_FILE_ALIASES),
                scenario_status=row_text(row, STATUS_ALIASES, "SCENARIO_AVAILABLE"),
                states_generated=row_int(row, STATES_GENERATED_ALIASES),
                transitions_generated=row_int(row, TRANSITIONS_GENERATED_ALIASES),
                timestamped_state_source_available=False,
                timestamped_transition_source_available=False,
                timestamped_context_row_count=0,
                scenario_context_coverage_class="TIMESTAMPED_CONTEXT_MISSING",
                scenario_diagnostic="Scenario inventory loaded; timestamped context coverage pending.",
            )
        )
    if rows:
        return rows
    return [
        ScenarioInventoryRow(
            scenario_id="SCENARIO_INPUT_MISSING",
            symbol=config.symbol,
            timeframe=config.timeframe,
            period_start="",
            period_end="",
            ohlc_file="",
            scenario_status="SCENARIO_INPUT_MISSING",
            states_generated=0,
            transitions_generated=0,
            timestamped_state_source_available=False,
            timestamped_transition_source_available=False,
            timestamped_context_row_count=0,
            scenario_context_coverage_class="SCENARIO_INPUT_MISSING",
            scenario_diagnostic="No scenario inventory file was available.",
        )
    ]


def enrich_scenario_inventory(
    scenarios: list[ScenarioInventoryRow],
    context_rows: list[TimestampedContextRow],
    state_scenario_ids: set[str],
    transition_scenario_ids: set[str],
) -> list[ScenarioInventoryRow]:
    counts = Counter(row.scenario_id for row in context_rows)
    enriched: list[ScenarioInventoryRow] = []
    for scenario in scenarios:
        count = counts.get(scenario.scenario_id, 0)
        state_available = scenario.scenario_id in state_scenario_ids
        transition_available = scenario.scenario_id in transition_scenario_ids
        coverage_class = _scenario_coverage_class(count, state_available, transition_available, scenario.scenario_status)
        enriched.append(
            ScenarioInventoryRow(
                scenario_id=scenario.scenario_id,
                symbol=scenario.symbol,
                timeframe=scenario.timeframe,
                period_start=scenario.period_start,
                period_end=scenario.period_end,
                ohlc_file=scenario.ohlc_file,
                scenario_status=scenario.scenario_status,
                states_generated=scenario.states_generated,
                transitions_generated=scenario.transitions_generated,
                timestamped_state_source_available=state_available,
                timestamped_transition_source_available=transition_available,
                timestamped_context_row_count=count,
                scenario_context_coverage_class=coverage_class,
                scenario_diagnostic=_scenario_diagnostic(coverage_class),
            )
        )
    return enriched


def _scenario_coverage_class(count: int, state_available: bool, transition_available: bool, status: str) -> str:
    if status == "SCENARIO_INPUT_MISSING":
        return "SCENARIO_INPUT_MISSING"
    if transition_available and count > 0:
        return "TIMESTAMPED_CONTEXT_AVAILABLE"
    if state_available or count > 0:
        return "PARTIAL_TIMESTAMPED_CONTEXT_AVAILABLE"
    return "TIMESTAMPED_CONTEXT_MISSING"


def _scenario_diagnostic(coverage_class: str) -> str:
    if coverage_class == "TIMESTAMPED_CONTEXT_AVAILABLE":
        return "Timestamped H4 context rows were generated for this scenario."
    if coverage_class == "PARTIAL_TIMESTAMPED_CONTEXT_AVAILABLE":
        return "Partial timestamped H4 context evidence is available for this scenario."
    if coverage_class == "SCENARIO_INPUT_MISSING":
        return "Scenario inventory input is missing."
    return "No timestamped H4 transition or state context rows were found for this scenario."
