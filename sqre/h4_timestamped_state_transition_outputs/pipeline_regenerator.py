"""Safe regeneration adapter for H4 timestamped state/transition outputs."""

from __future__ import annotations

from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.models import RegenerationResult, ScenarioInventoryRow


def evaluate_regeneration_support(
    scenarios: list[ScenarioInventoryRow],
    config: H4TimestampedStateTransitionConfig,
) -> list[RegenerationResult]:
    """Classify whether local regeneration can be attempted without downloads.

    This adapter is intentionally conservative. It never downloads data and does not
    call production state/transition pipelines unless a future phase wires a safe
    export path for per-scenario timestamped artifacts.
    """

    results: list[RegenerationResult] = []
    for scenario in scenarios:
        if not config.allow_regeneration:
            results.append(_result(scenario.scenario_id, False, "SKIPPED_REGENERATION_DISABLED"))
            continue
        if not scenario.raw_ohlc_file or not _raw_exists(scenario.raw_ohlc_file):
            results.append(_result(scenario.scenario_id, True, "SKIPPED_RAW_OHLC_MISSING"))
            continue
        results.append(_result(scenario.scenario_id, True, "SKIPPED_REGENERATION_NOT_AVAILABLE"))
    return results


def _raw_exists(raw_ohlc_file: str) -> bool:
    path = Path(raw_ohlc_file)
    return path.exists()


def _result(scenario_id: str, attempted: bool, status: str) -> RegenerationResult:
    diagnostics = {
        "SKIPPED_REGENERATION_DISABLED": "Regeneration was disabled by configuration.",
        "SKIPPED_RAW_OHLC_MISSING": "Local raw OHLC file is missing; no data download was attempted.",
        "SKIPPED_REGENERATION_NOT_AVAILABLE": "Safe per-scenario export adapter is not available in this phase.",
    }
    return RegenerationResult(
        scenario_id=scenario_id,
        attempted=attempted,
        status=status,
        diagnostic=diagnostics.get(status, "Regeneration status was classified."),
    )
