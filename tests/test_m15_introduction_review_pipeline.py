import pandas as pd

from sqre.m15_introduction_review import run_m15_introduction_review


def test_pipeline_writes_summary_and_report(tmp_path):
    input_path = tmp_path / "m15_summary.csv"
    output_path = tmp_path / "m15_review.csv"
    report_path = tmp_path / "m15_review.txt"
    input_path.write_text(
        "\n".join(
            [
                _header(),
                "eurusd_m15_period_1,M15,COMPLETED,100,10,7200,5,DIRECTIONAL_DRIFT,8,0.4,4,3,10,5",
                "eurusd_m15_period_2,M15,COMPLETED,120,12,8200,6,VOLATILE_ROTATION,10,0.5,6,4,12,6",
            ]
        ),
        encoding="utf-8",
    )

    result = run_m15_introduction_review(
        m15_summary_csv=input_path,
        output_path=output_path,
        report_path=report_path,
    )

    frame = pd.read_csv(output_path)
    assert result.rows_loaded == 2
    assert result.scenarios_reviewed == 2
    assert list(frame["Timeframe"]) == ["M15"]
    assert report_path.exists()


def _header() -> str:
    return (
        "Scenario_ID,Timeframe,Status,OHLC_Rows,Structures_Detected,Average_Structure_Duration,"
        "Unique_States,Most_Common_State,Average_Forward_Range_Pips,Direction_Alignment_Rate,"
        "Low_Sample_Conditions_Research,Low_Sample_Conditions_Price_Outcome,States_Generated,"
        "Directional_Displacement_Count"
    )
