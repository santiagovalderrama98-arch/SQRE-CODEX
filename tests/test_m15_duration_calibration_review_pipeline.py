import pandas as pd

from sqre.m15_duration_calibration_review import run_m15_duration_calibration_review


def test_pipeline_writes_review_summary_and_report(tmp_path):
    input_path = tmp_path / "experiment_summary.csv"
    output_path = tmp_path / "review.csv"
    report_path = tmp_path / "review.txt"
    input_path.write_text(
        "\n".join(
            [
                _header(),
                "eurusd_m15_period_1,M15,m15_duration_8h_baseline,COMPLETED,28800,20,24000,7,"
                "DIRECTIONAL_DRIFT,8,0.4,50,20,20,5",
                "eurusd_m15_period_1,M15,m15_duration_4h,COMPLETED,14400,30,12000,7,"
                "DIRECTIONAL_DRIFT,8,0.4,60,20,30,6",
            ]
        ),
        encoding="utf-8",
    )

    result = run_m15_duration_calibration_review(input_path, output_path, report_path)

    frame = pd.read_csv(output_path)
    assert result.rows_loaded == 2
    assert result.profiles_reviewed == 2
    assert set(frame["Experiment_Profile"]) == {"m15_duration_8h_baseline", "m15_duration_4h"}
    assert report_path.exists()


def _header() -> str:
    return (
        "Scenario_ID,Timeframe,Experiment_Profile,Status,Max_Structure_Duration_Seconds,"
        "Structures_Detected,Average_Structure_Duration,Unique_States,Most_Common_State,"
        "Average_Forward_Range_Pips,Direction_Alignment_Rate,Low_Sample_Conditions_Research,"
        "Low_Sample_Conditions_Price_Outcome,States_Generated,Directional_Displacement_Count"
    )
