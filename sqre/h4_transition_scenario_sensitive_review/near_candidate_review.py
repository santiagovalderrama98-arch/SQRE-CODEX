"""Near-candidate and focus profile outputs for H4 transition review."""

from __future__ import annotations

from dataclasses import asdict

from sqre.h4_transition_scenario_sensitive_review.models import (
    FocusProfileReview,
    NearAggregationCandidate,
    ProfileReviewRow,
)


def build_near_aggregation_candidates(rows: list[ProfileReviewRow]) -> list[NearAggregationCandidate]:
    return [
        NearAggregationCandidate(
            **asdict(row),
            near_candidate_rationale="Profile meets descriptive near-candidate criteria without automatic filtering.",
        )
        for row in rows
        if row.near_aggregation_candidate_flag == "YES"
    ]


def build_focus_profile_review(rows: list[ProfileReviewRow]) -> list[FocusProfileReview]:
    return [
        FocusProfileReview(
            **asdict(row),
            focus_profile_rationale="Profile belongs to the configured transition focus set.",
        )
        for row in rows
        if row.focus_transition_flag == "YES"
    ]
