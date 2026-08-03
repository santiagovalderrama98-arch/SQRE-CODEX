from pathlib import Path

from sqre.h4_timestamped_state_transition_outputs.config import H4TimestampedStateTransitionConfig
from sqre.h4_timestamped_state_transition_outputs.scenario_resolver import load_scenarios


def test_scenario_resolver_loads_validation_summary(tmp_path: Path):
    validation = tmp_path / "validation"
    research = tmp_path / "research"
    validation.mkdir()
    research.mkdir()
    (validation / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,Symbol,Timeframe,Period_Start,Period_End,States_Generated,Transitions_Generated\n"
        "SCN_1,EURUSD,H4,2026-01-01,2026-01-31,2,1\n",
        encoding="utf-8",
    )
    config = H4TimestampedStateTransitionConfig(
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=research,
        validation_config=tmp_path / "missing.yaml",
    )

    scenarios = load_scenarios(config)

    assert len(scenarios) == 1
    assert scenarios[0].scenario_id == "SCN_1"
    assert scenarios[0].expected_state_count == 2
    assert scenarios[0].expected_transition_count == 1


def test_scenario_resolver_uses_config_fallback_when_available(tmp_path: Path):
    validation = tmp_path / "validation"
    research = tmp_path / "research"
    validation.mkdir()
    research.mkdir()
    config_path = tmp_path / "validation.yaml"
    config_path.write_text(
        "scenarios:\n"
        "  - scenario_id: SCN_CFG\n"
        "    symbol: EURUSD\n"
        "    timeframe: H4\n"
        "    period_start: 2026-01-01\n"
        "    period_end: 2026-01-31\n",
        encoding="utf-8",
    )
    config = H4TimestampedStateTransitionConfig(
        h4_d1_validation_dir=validation,
        h4_d1_structural_research_dir=research,
        validation_config=config_path,
    )

    scenarios = load_scenarios(config)

    assert [row.scenario_id for row in scenarios] == ["SCN_CFG"]
