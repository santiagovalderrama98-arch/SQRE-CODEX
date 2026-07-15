"""Sequence-level H4/D1 structural research profiles."""

from __future__ import annotations

from collections import defaultdict

from sqre.h4_d1_structural_research.config import H4D1StructuralResearchConfig
from sqre.h4_d1_structural_research.consistency import adequacy_flag, mean
from sqre.h4_d1_structural_research.loader import read_csv, resolve_column
from sqre.h4_d1_structural_research.models import ScenarioData, SequenceResearchProfile


def build_sequence_research_profiles(
    scenarios: list[ScenarioData],
    config: H4D1StructuralResearchConfig,
) -> list[SequenceResearchProfile]:
    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)

    for scenario in scenarios:
        inventory = scenario.inventory
        frame = read_csv(scenario.sequence_outcomes_path)
        sequence_column = resolve_column(frame, "Sequence") or resolve_column(frame, "Sequence_Label")
        count_column = resolve_column(frame, "Count")
        if frame.empty or sequence_column is None:
            continue
        for sequence, group in frame.groupby(sequence_column):
            count = int(group[count_column].sum()) if count_column is not None else len(group)
            key = (inventory.timeframe, str(sequence))
            counts[key][inventory.scenario_id] = counts[key].get(inventory.scenario_id, 0) + count

    profiles: list[SequenceResearchProfile] = []
    for key, by_scenario in sorted(counts.items()):
        timeframe, sequence = key
        scenario_ids = sorted(by_scenario)
        values = list(by_scenario.values())
        total = sum(values)
        flag = adequacy_flag(total, config.minimum_sample_size)
        profiles.append(
            SequenceResearchProfile(
                timeframe=timeframe,
                sequence_label=sequence,
                scenario_count=len(scenario_ids),
                scenarios_present=";".join(scenario_ids),
                total_sequence_count=total,
                average_sequence_count_per_scenario=mean(values),
                sequence_sample_adequacy_flag=flag,
                sequence_profile_diagnostic=_diagnostic(sequence, flag),
            )
        )
    return profiles


def _diagnostic(sequence: str, sample_flag: str) -> str:
    if sample_flag == "LOW_SAMPLE":
        return f"{sequence} sequence profile requires sample adequacy review"
    return f"{sequence} sequence profile is available for descriptive review"
