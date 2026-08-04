import pandas as pd

from sqre.research_reference_store_usage_review.config import ResearchReferenceStoreUsageReviewConfig
from sqre.research_reference_store_usage_review.findings import build_summary


def test_findings_mark_ready_when_core_reference_coverage_is_high():
    summary = build_summary(
        reference_store=pd.DataFrame([{"Research_Reference_ID": "REF_1"}]),
        usage_scenarios=pd.DataFrame([{"Scenario_Source": "HISTORICAL_ALIGNMENT_SCENARIO"}]),
        lookup_results=pd.DataFrame(
            [
                {
                    "Reference_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_MATCH",
                    "Reference_Match_Quality_Class": "HIGH_QUALITY_REFERENCE_MATCH",
                    "Reference_Evidence_Quality_Class": "CORE_REFERENCE_EVIDENCE",
                }
            ]
        ),
        availability_review=pd.DataFrame([{"Reference_Availability_Ratio": 1.0}]),
        granularity_usage_review=pd.DataFrame(
            [
                {
                    "Reference_Match_Level": "EXACT_D1_STATE_REGIME_CONTEXT_MATCH",
                    "Granularity_Usage_Class": "PRIMARY_USAGE_GRANULARITY",
                    "Core_Reference_Count": 1,
                    "Supporting_Reference_Count": 0,
                    "Matched_Scenario_Count": 1,
                }
            ]
        ),
        horizon_usage_review=pd.DataFrame(
            [
                {
                    "Forward_Horizon_H4_Candles": 1,
                    "Horizon_Usage_Class": "PRIMARY_USAGE_HORIZON",
                    "Core_Reference_Count": 1,
                    "Supporting_Reference_Count": 0,
                    "Matched_Scenario_Count": 1,
                }
            ]
        ),
        config=ResearchReferenceStoreUsageReviewConfig(),
    )

    assert summary.dominant_reference_usage_readiness_class == "REFERENCE_USAGE_READY"
    assert summary.research_reference_store_usage_readiness_flag == "READY_FOR_RESEARCH_QUERY_INTERFACE_DESIGN"


def test_findings_mark_input_limited_when_no_references():
    summary = build_summary(
        pd.DataFrame(),
        pd.DataFrame([{"Scenario_Source": "INPUT_MISSING"}]),
        pd.DataFrame(),
        pd.DataFrame([{"Reference_Availability_Ratio": 0.0}]),
        pd.DataFrame(),
        pd.DataFrame(),
        ResearchReferenceStoreUsageReviewConfig(),
    )

    assert summary.dominant_reference_usage_readiness_class == "REFERENCE_USAGE_INPUT_LIMITED"
