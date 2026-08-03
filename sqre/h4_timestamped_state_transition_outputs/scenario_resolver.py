"""Scenario resolution for H4 timestamped state/transition output generation."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.loader import (
    OHLC_FILE_ALIASES,
    PERIOD_END_ALIASES,
    PERIOD_START_ALIASES,
    SCENARIO_ALIASES,
    STATES_GENERATED_ALIASES,
    STATUS_ALIASES,
    SYMBOL_ALIASES,
    TIMEFRAME_ALIASES,
    TRANSITIONS_GENERATED_ALIASES,
    read_optional_csv,
    row_int,
    row_text,
)
from sqre.h4_timestamped_state_transition_outputs.models import ScenarioInventoryRow


def load_scenarios(config: H4TimestampedStateTransitionConfig) -> list[ScenarioInventoryRow]:
    """Load H4 scenario metadata from validation CSV, research CSV, or config fallback."""

    rows = _load_csv_scenarios(config.h4_d1_validation_dir / "h4_d1_validation_summary.csv", config)
    if not rows:
        rows = _load_csv_scenarios(config.h4_d1_structural_research_dir / "h4_d1_scenario_inventory.csv", config)
    if not rows:
        rows = _load_config_scenarios(config.validation_config, config)
    if rows:
        return rows
    return [
        ScenarioInventoryRow(
            scenario_id="SCENARIO_INPUT_MISSING",
            symbol=config.symbol,
            timeframe=config.timeframe,
            period_start="",
            period_end="",
            scenario_status="SCENARIO_INPUT_MISSING",
            expected_state_count=0,
            expected_transition_count=0,
            raw_ohlc_file="",
            raw_ohlc_available=False,
            existing_state_output_available=False,
            existing_transition_output_available=False,
            regeneration_attempted=False,
            regeneration_status="SKIPPED_SCENARIO_INPUT_MISSING",
            timestamped_state_row_count=0,
            timestamped_transition_row_count=0,
            scenario_output_coverage_class="SCENARIO_INPUT_MISSING",
            scenario_diagnostic="No scenario inventory source was available.",
        )
    ]


def with_runtime_counts(
    scenarios: list[ScenarioInventoryRow],
    state_counts: dict[str, int],
    transition_counts: dict[str, int],
    regeneration_status: dict[str, tuple[bool, str]],
) -> list[ScenarioInventoryRow]:
    """Attach observed output counts and status to scenario inventory rows."""

    enriched: list[ScenarioInventoryRow] = []
    for scenario in scenarios:
        state_count = state_counts.get(scenario.scenario_id, 0)
        transition_count = transition_counts.get(scenario.scenario_id, 0)
        attempted, status = regeneration_status.get(
            scenario.scenario_id,
            (False, "SKIPPED_REGENERATION_NOT_NEEDED"),
        )
        coverage_class = _scenario_coverage_class(
            state_count,
            transition_count,
            scenario.scenario_status,
            status,
        )
        enriched.append(
            ScenarioInventoryRow(
                scenario_id=scenario.scenario_id,
                symbol=scenario.symbol,
                timeframe=scenario.timeframe,
                period_start=scenario.period_start,
                period_end=scenario.period_end,
                scenario_status=scenario.scenario_status,
                expected_state_count=scenario.expected_state_count,
                expected_transition_count=scenario.expected_transition_count,
                raw_ohlc_file=scenario.raw_ohlc_file,
                raw_ohlc_available=scenario.raw_ohlc_available,
                existing_state_output_available=state_count > 0,
                existing_transition_output_available=transition_count > 0,
                regeneration_attempted=attempted,
                regeneration_status=status,
                timestamped_state_row_count=state_count,
                timestamped_transition_row_count=transition_count,
                scenario_output_coverage_class=coverage_class,
                scenario_diagnostic=_scenario_diagnostic(coverage_class, status),
            )
        )
    return enriched


def _load_csv_scenarios(path: Path, config: H4TimestampedStateTransitionConfig) -> list[ScenarioInventoryRow]:
    frame = read_optional_csv(path)
    if frame.empty:
        return []
    rows: list[ScenarioInventoryRow] = []
    for index, row in frame.iterrows():
        timeframe = row_text(row, TIMEFRAME_ALIASES, config.timeframe) or config.timeframe
        if timeframe.upper() != config.timeframe.upper():
            continue
        raw_ohlc_file = row_text(row, OHLC_FILE_ALIASES)
        rows.append(
            _base_scenario(
                scenario_id=row_text(row, SCENARIO_ALIASES, f"SCENARIO_{index + 1:06d}"),
                symbol=row_text(row, SYMBOL_ALIASES, config.symbol) or config.symbol,
                timeframe=timeframe,
                period_start=row_text(row, PERIOD_START_ALIASES),
                period_end=row_text(row, PERIOD_END_ALIASES),
                scenario_status=row_text(row, STATUS_ALIASES, "SCENARIO_AVAILABLE"),
                raw_ohlc_file=raw_ohlc_file,
                raw_ohlc_available=_raw_exists(raw_ohlc_file, path.parent),
                states_generated=row_int(row, STATES_GENERATED_ALIASES),
                transitions_generated=row_int(row, TRANSITIONS_GENERATED_ALIASES),
            )
        )
    return rows


def _load_config_scenarios(path: Path, config: H4TimestampedStateTransitionConfig) -> list[ScenarioInventoryRow]:
    if not path.exists():
        return []
    rows: list[ScenarioInventoryRow] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current:
                row = _config_row(current, path.parent, config)
                if row:
                    rows.append(row)
            current = {}
            line = line[2:].strip()
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip().lower()] = value.strip().strip("'\"")
    if current:
        row = _config_row(current, path.parent, config)
        if row:
            rows.append(row)
    return rows


def _config_row(
    raw: dict[str, str],
    base_dir: Path,
    config: H4TimestampedStateTransitionConfig,
) -> ScenarioInventoryRow | None:
    timeframe = raw.get("timeframe", config.timeframe) or config.timeframe
    if timeframe.upper() != config.timeframe.upper():
        return None
    raw_ohlc_file = raw.get("ohlc_file") or raw.get("raw_ohlc_file") or raw.get("raw_file", "")
    return _base_scenario(
        scenario_id=raw.get("scenario_id") or raw.get("id") or "SCENARIO_FROM_CONFIG",
        symbol=raw.get("symbol", config.symbol) or config.symbol,
        timeframe=timeframe,
        period_start=raw.get("period_start") or raw.get("start") or raw.get("start_date", ""),
        period_end=raw.get("period_end") or raw.get("end") or raw.get("end_date", ""),
        scenario_status=raw.get("scenario_status") or raw.get("status") or "SCENARIO_FROM_CONFIG",
        raw_ohlc_file=raw_ohlc_file,
        raw_ohlc_available=_raw_exists(raw_ohlc_file, base_dir),
        states_generated=int(float(raw.get("states_generated", "0") or 0)),
        transitions_generated=int(float(raw.get("transitions_generated", "0") or 0)),
    )


def _base_scenario(
    *,
    scenario_id: str,
    symbol: str,
    timeframe: str,
    period_start: str,
    period_end: str,
    scenario_status: str,
    raw_ohlc_file: str,
    raw_ohlc_available: bool,
    states_generated: int,
    transitions_generated: int,
) -> ScenarioInventoryRow:
    return ScenarioInventoryRow(
        scenario_id=scenario_id,
        symbol=symbol,
        timeframe=timeframe,
        period_start=period_start,
        period_end=period_end,
        scenario_status=scenario_status,
        expected_state_count=states_generated,
        expected_transition_count=transitions_generated,
        raw_ohlc_file=raw_ohlc_file,
        raw_ohlc_available=raw_ohlc_available,
        existing_state_output_available=False,
        existing_transition_output_available=False,
        regeneration_attempted=False,
        regeneration_status="SKIPPED_REGENERATION_PENDING",
        timestamped_state_row_count=0,
        timestamped_transition_row_count=0,
        scenario_output_coverage_class="TIMESTAMPED_OUTPUTS_MISSING",
        scenario_diagnostic=f"Scenario loaded with expected states={states_generated} and transitions={transitions_generated}.",
    )


def _raw_exists(raw_ohlc_file: str, base_dir: Path) -> bool:
    if not raw_ohlc_file:
        return False
    path = Path(raw_ohlc_file)
    return path.exists() or (base_dir / path).exists()


def _scenario_coverage_class(state_count: int, transition_count: int, status: str, regeneration_status: str) -> str:
    if status == "SCENARIO_INPUT_MISSING":
        return "SCENARIO_INPUT_MISSING"
    if state_count > 0 and transition_count > 0:
        return "TIMESTAMPED_STATES_AND_TRANSITIONS_AVAILABLE"
    if state_count > 0:
        return "TIMESTAMPED_STATES_ONLY_AVAILABLE"
    if transition_count > 0:
        return "TIMESTAMPED_TRANSITIONS_ONLY_AVAILABLE"
    if regeneration_status == "REGENERATED_TIMESTAMPED_OUTPUTS_AVAILABLE":
        return "REGENERATED_TIMESTAMPED_OUTPUTS_AVAILABLE"
    return "TIMESTAMPED_OUTPUTS_MISSING"


def _scenario_diagnostic(coverage_class: str, regeneration_status: str) -> str:
    if coverage_class == "TIMESTAMPED_STATES_AND_TRANSITIONS_AVAILABLE":
        return "Timestamped state and transition outputs are available for this scenario."
    if coverage_class == "TIMESTAMPED_STATES_ONLY_AVAILABLE":
        return "Timestamped states are available; timestamped transitions are missing."
    if coverage_class == "TIMESTAMPED_TRANSITIONS_ONLY_AVAILABLE":
        return "Timestamped transitions are available; timestamped states are missing."
    if coverage_class == "SCENARIO_INPUT_MISSING":
        return "Scenario input metadata is missing."
    return f"Timestamped state/transition outputs are missing; regeneration status: {regeneration_status}."
