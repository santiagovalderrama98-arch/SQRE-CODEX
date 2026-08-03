from pathlib import Path
from subprocess import run


def test_h4_timestamped_state_transition_cli_works_with_synthetic_temp_data(tmp_path: Path):
    validation = tmp_path / "validation"
    scenario_dir = validation / "scenario"
    research = tmp_path / "research"
    out = tmp_path / "out"
    scenario_dir.mkdir(parents=True)
    research.mkdir()
    (validation / "h4_d1_validation_summary.csv").write_text(
        "Scenario_ID,Symbol,Timeframe,Period_Start,Period_End,States_Generated,Transitions_Generated\n"
        "SCN_1,EURUSD,H4,2026-01-01,2026-01-31,1,1\n",
        encoding="utf-8",
    )
    (scenario_dir / "state_transitions.csv").write_text(
        "Scenario_ID,Transition_Time,Source_State,Target_State,Transition_Label,Timeframe\n"
        "SCN_1,2026-01-01 04:00:00,A,B,A -> B,H4\n",
        encoding="utf-8",
    )

    completed = run(
        [
            "python3",
            "scripts/run_h4_timestamped_state_transition_outputs.py",
            "--h4-d1-validation-dir",
            str(validation),
            "--h4-d1-structural-research-dir",
            str(research),
            "--validation-config",
            str(tmp_path / "missing.yaml"),
            "--output-dir",
            str(out),
            "--report",
            str(out / "report.txt"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "H4 timestamped state/transition output generation completed" in completed.stdout
    assert (out / "h4_timestamped_state_transitions.csv").exists()
