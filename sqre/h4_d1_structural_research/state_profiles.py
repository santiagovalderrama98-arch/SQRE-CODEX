"""State-level H4/D1 structural research profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.consistency import adequacy_flag, consistency_flag, cv, mean, ratio
from sqre.h4_d1_structural_research.loader import read_csv, resolve_column
from sqre.h4_d1_structural_research.models import ScenarioData, StateResearchProfile


def build_state_research_profiles(
    scenarios: list[ScenarioData],
    config: H4D1StructuralResearchConfig,
) -> list[StateResearchProfile]:
    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    confidences: dict[tuple[str, str], list[float]] = defaultdict(list)
    total_states: dict[str, int] = defaultdict(int)
    scenario_ids_by_timeframe: dict[str, list[str]] = defaultdict(list)

    for scenario in scenarios:
        inventory = scenario.inventory
        scenario_ids_by_timeframe[inventory.timeframe].append(inventory.scenario_id)
        frame = read_csv(scenario.market_states_path)
        state_column = resolve_column(frame, "Market_State")
        confidence_column = resolve_column(frame, "State_Confidence")
        if frame.empty or state_column is None:
            continue
        total_states[inventory.timeframe] += len(frame)
        for state, group in frame.groupby(state_column):
            key = (inventory.timeframe, str(state))
            counts[key][inventory.scenario_id] = len(group)
            if confidence_column is not None:
                values = group[confidence_column]
                confidences[key].extend(float(value) for value in values if _is_number(value))

    profiles: list[StateResearchProfile] = []
    for key, by_scenario in sorted(counts.items()):
        timeframe, market_state = key
        scenario_ids = sorted(by_scenario)
        all_counts = [by_scenario.get(scenario_id, 0) for scenario_id in scenario_ids_by_timeframe[timeframe]]
        total_count = sum(all_counts)
        scenario_cv = cv(all_counts)
        sample_flag = adequacy_flag(total_count, config.minimum_sample_size)
        consistency = consistency_flag(scenario_cv, config.high_scenario_cv_threshold)
        profiles.append(
            StateResearchProfile(
                timeframe=timeframe,
                market_state=market_state,
                scenario_count=len(scenario_ids),
                scenarios_present=";".join(scenario_ids),
                total_state_count=total_count,
                average_state_count_per_scenario=mean(all_counts),
                state_frequency_ratio=ratio(total_count, total_states[timeframe]),
                average_state_confidence=mean(confidences[key]),
                scenario_count_cv=scenario_cv,
                state_sample_adequacy_flag=sample_flag,
                state_scenario_consistency_flag=consistency,
                state_profile_diagnostic=_diagnostic(market_state, sample_flag, consistency),
            )
        )
    return profiles


def _diagnostic(market_state: str, sample_flag: str, consistency: str) -> str:
    if sample_flag == "LOW_SAMPLE":
        return f"{market_state} state profile requires sample adequacy review"
    if consistency == "VARIABLE":
        return f"{market_state} state profile varies across scenarios"
    return f"{market_state} state profile is descriptively consistent"


def _is_number(value: object) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
