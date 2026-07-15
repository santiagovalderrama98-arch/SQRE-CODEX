"""Transition-level H4/D1 structural research profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.consistency import adequacy_flag, consistency_flag, cv, mean, ratio
from sqre.h4_d1_structural_research.loader import read_csv, resolve_column
from sqre.h4_d1_structural_research.models import ScenarioData, TransitionResearchProfile


def build_transition_research_profiles(
    scenarios: list[ScenarioData],
    config: H4D1StructuralResearchConfig,
) -> list[TransitionResearchProfile]:
    counts: dict[tuple[str, str, str, str], dict[str, int]] = defaultdict(dict)
    total_transitions: dict[str, int] = defaultdict(int)
    scenario_ids_by_timeframe: dict[str, list[str]] = defaultdict(list)

    for scenario in scenarios:
        inventory = scenario.inventory
        scenario_ids_by_timeframe[inventory.timeframe].append(inventory.scenario_id)
        frame = read_csv(scenario.transitions_path)
        label_column = resolve_column(frame, "Transition_Label")
        from_column = resolve_column(frame, "From_Market_State")
        to_column = resolve_column(frame, "To_Market_State")
        if frame.empty or label_column is None:
            continue
        total_transitions[inventory.timeframe] += len(frame)
        for _, row in frame.iterrows():
            label = str(row[label_column])
            from_state = str(row[from_column]) if from_column is not None else _from_label(label)
            to_state = str(row[to_column]) if to_column is not None else _to_label(label)
            key = (inventory.timeframe, from_state, to_state, label)
            counts[key][inventory.scenario_id] = counts[key].get(inventory.scenario_id, 0) + 1

    profiles: list[TransitionResearchProfile] = []
    for key, by_scenario in sorted(counts.items()):
        timeframe, from_state, to_state, label = key
        scenario_ids = sorted(by_scenario)
        all_counts = [by_scenario.get(scenario_id, 0) for scenario_id in scenario_ids_by_timeframe[timeframe]]
        total_count = sum(all_counts)
        scenario_cv = cv(all_counts)
        sample_flag = adequacy_flag(total_count, config.minimum_sample_size)
        consistency = consistency_flag(scenario_cv, config.high_scenario_cv_threshold)
        profiles.append(
            TransitionResearchProfile(
                timeframe=timeframe,
                from_state=from_state,
                to_state=to_state,
                transition_label=label,
                scenario_count=len(scenario_ids),
                scenarios_present=";".join(scenario_ids),
                total_transition_count=total_count,
                average_transition_count_per_scenario=mean(all_counts),
                transition_frequency_ratio=ratio(total_count, total_transitions[timeframe]),
                scenario_count_cv=scenario_cv,
                transition_sample_adequacy_flag=sample_flag,
                transition_consistency_flag=consistency,
                transition_profile_diagnostic=_diagnostic(label, sample_flag, consistency),
            )
        )
    return profiles


def _diagnostic(label: str, sample_flag: str, consistency: str) -> str:
    if sample_flag == "LOW_SAMPLE":
        return f"{label} transition profile requires sample adequacy review"
    if consistency == "VARIABLE":
        return f"{label} transition profile varies across scenarios"
    return f"{label} transition profile is descriptively consistent"


def _from_label(label: str) -> str:
    return label.split("->", 1)[0].split("_TO_", 1)[0].strip()


def _to_label(label: str) -> str:
    if "->" in label:
        return label.split("->", 1)[1].strip()
    if "_TO_" in label:
        return label.split("_TO_", 1)[1].strip()
    return ""
