from pathlib import Path

from sqre.d1_regime_outcome_review.d1_regime_outcome_review_pipeline import run_d1_regime_outcome_review


def test_review_report_contains_required_sections_and_safe_language(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    report_path = output_dir / "d1_regime_outcome_review_report.txt"
    _write_profiles(input_dir)

    run_d1_regime_outcome_review(input_dir, output_dir, report_path)

    report = report_path.read_text(encoding="utf-8")
    assert "SQRE D1 Regime Outcome Dispersion & Sample Adequacy Review" in report
    assert "Executive Diagnostic Summary" in report
    assert "Condition Quality Overview" in report
    assert "Research-Ready Descriptive Profiles" in report
    assert "Regime-Sensitive Profiles" in report
    assert "Low-Sample / Limited-Coverage Review" in report
    assert "State Condition Review" in report
    assert "Transition Condition Review" in report
    assert "Outcome Dispersion Review" in report
    assert "Research Readiness Assessment" in report
    assert "Potential Follow-Up Areas" in report
    assert "Do Not Change Yet" in report
    assert "Limitations" in report
    assert "No comparative ordering is produced." in report

    forbidden = [
        "buy",
        "sell",
        "entry",
        "exit",
        "trade signal",
        "trade setup",
        "take profit",
        "stop loss",
        "profitable",
        "opportunity",
        "edge",
        "best timeframe",
        "ranking",
        "should trade",
        "predicts",
        "optimal",
    ]
    lowered = report.lower()
    assert not [term for term in forbidden if term in lowered]


def _write_profiles(input_dir: Path) -> None:
    input_dir.mkdir()
    (input_dir / "d1_regime_normalized_condition_profiles.csv").write_text(
        "\n".join(
            [
                "Condition_Type,Condition_Label,Forward_Window,Regime_Count,Total_Sample_Size,"
                "Average_Forward_Range_Pips,Average_Outcome_Magnitude_Pips,Average_Direction_Alignment_Rate,"
                "Forward_Range_CV,Outcome_Magnitude_CV,Regime_Sensitivity_Flag",
                "STATE,EXPANSION,20,4,80,22.5,8.0,0.61,0.12,0.18,STABLE",
                "TRANSITION,A_TO_B,20,4,90,24.5,9.0,0.57,0.42,0.18,HIGH",
            ]
        ),
        encoding="utf-8",
    )
