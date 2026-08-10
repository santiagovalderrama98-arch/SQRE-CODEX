"""Markdown renderer for reference stability documentation."""

from __future__ import annotations

import pandas as pd

from sqre.reference_stability_documentation.config import ReferenceStabilityDocumentationConfig
from sqre.reference_stability_documentation.models import ReferenceStabilityDocumentationSummary


def render_markdown(
    config: ReferenceStabilityDocumentationConfig,
    interpretation: pd.DataFrame,
    usage_policy: pd.DataFrame,
    dashboard_guide: pd.DataFrame,
    limitations: pd.DataFrame,
    follow_up: pd.DataFrame,
    summary: ReferenceStabilityDocumentationSummary | None,
) -> str:
    title = config.documentation_title
    lines = [
        f"# {title}",
        "",
        "## Purpose",
        "SQRE reference stability findings are descriptive research diagnostics.",
        "This document explains how to read reference stability outputs for manual research review.",
        "",
        "## Current Evidence Base",
        *_summary_lines(summary),
        "",
        "## Stability Summary",
        *_table_lines(interpretation, "Stability_Dimension", "Documentation_Class"),
        "",
        "## How to Read Stable Evidence",
        "Stable sample size and stable dispersion do not imply predictive edge.",
        "Stable rows may be reviewed as historical research references with clear context labels.",
        "",
        "## How to Read Partial Evidence",
        "Partial horizon stability means evidence should be compared across horizons cautiously.",
        "Partial granularity stability means overly specific contexts may fragment the evidence.",
        "",
        "## How to Read Directionally Unstable Evidence",
        "Directional instability means directional behavior should not be over-interpreted.",
        "",
        "## How to Read Fallback-Dependent Evidence",
        "Fallback-dependent matches should be displayed with clear evidence warnings.",
        "",
        "## Dashboard Reading Guide",
        "Dashboard cards are research references, not trading instructions.",
        *_table_lines(dashboard_guide, "Dashboard_Element", "Dashboard_Reading_Guide_Class"),
        "",
        "## What the Dashboard Must Not Be Used For",
        "The dashboard is not live market data unless explicitly connected in a later phase.",
        "This phase does not generate trading signals.",
        "This phase does not generate operational recommendations.",
        "This phase does not create a Decision Engine.",
        "",
        "## Limitations",
        *_table_lines(limitations, "Limitation_Category", "Limitation_Text"),
        "",
        "## Recommended Follow-Up",
        *_table_lines(follow_up, "Follow_Up_Category", "Follow_Up_Priority"),
        "",
        "## Scope Statements",
        "Documentation findings are descriptive research guidance only.",
        "This phase does not decide whether any context is favorable or unfavorable.",
        "This phase does not perform profitability analysis.",
        "No production defaults were modified.",
        "No thresholds were modified.",
        "No production taxonomy was modified.",
    ]
    return "\n".join(lines) + "\n"


def _summary_lines(summary: ReferenceStabilityDocumentationSummary | None) -> list[str]:
    if summary is None:
        return ["No documentation summary was produced."]
    return [
        f"- Symbol: {summary.symbol}",
        f"- H4 timeframe: {summary.h4_timeframe}",
        f"- D1 timeframe: {summary.d1_timeframe}",
        f"- Documentation readiness: {summary.reference_stability_documentation_readiness_class}",
        f"- Readiness flag: {summary.reference_stability_documentation_readiness_flag}",
    ]


def _table_lines(frame: pd.DataFrame, key_column: str, value_column: str) -> list[str]:
    if frame.empty:
        return ["No rows were produced."]
    return [f"- {row.get(key_column, '')}: {row.get(value_column, '')}" for _, row in frame.iterrows()]
