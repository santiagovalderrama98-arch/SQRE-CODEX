"""Near-candidate review for scenario-sensitive H4 profiles."""

from __future__ import annotations

from dataclasses import asdict

from sqre.h4_scenario_sensitive_state_review.models import NearAggregationCandidate, ProfileReviewRow


def build_near_aggregation_candidates(rows: list[ProfileReviewRow]) -> list[NearAggregationCandidate]:
    return [
        NearAggregationCandidate(
            **asdict(row),
            near_candidate_rationale="Profile meets descriptive near-candidate criteria without automatic filtering.",
        )
        for row in rows
        if row.near_aggregation_candidate_flag == "YES"
    ]
