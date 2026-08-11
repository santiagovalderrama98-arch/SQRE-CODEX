"""Self-contained HTML renderer for dashboard stability indicators."""

from __future__ import annotations

from html import escape

import pandas as pd

from sqre.dashboard_stability_indicators.config import DashboardStabilityIndicatorsConfig
from sqre.dashboard_stability_indicators.findings import limitation_lines, scope_statements
from sqre.dashboard_stability_indicators.models import DashboardStabilityIndicatorsSummary


def render_html(
    config: DashboardStabilityIndicatorsConfig,
    summary: DashboardStabilityIndicatorsSummary | None,
    legend: pd.DataFrame,
    reference_cards: pd.DataFrame,
    evidence_panel: pd.DataFrame,
    behavior_panel: pd.DataFrame,
    fallback_panel: pd.DataFrame,
    warning_summary: pd.DataFrame,
) -> str:
    """Render static HTML with stability labels and research-only guardrails."""

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(config.dashboard_title)}</title>",
            "<style>",
            _style(),
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            f"<h1>{escape(config.dashboard_title)}</h1>",
            '<section class="notice">',
            "<p>All labels in this file are research-only stability indicators.</p>",
            "<p>These indicators are not live market data unless a later phase explicitly connects a live source.</p>",
            "</section>",
            _summary_section(summary),
            _table_section("Indicator Legend", legend),
            _table_section("Stability-Aware Reference Cards", reference_cards),
            _table_section("Evidence Stability Panel", evidence_panel),
            _table_section("Behavior Stability Panel", behavior_panel),
            _table_section("Fallback Stability Panel", fallback_panel),
            _table_section("Warning Summary", warning_summary),
            _list_section("Limitations", limitation_lines()),
            _list_section("Scope Statements", scope_statements()),
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _style() -> str:
    return """
body {
  background: #f6f7f9;
  color: #17202a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.45;
  margin: 0;
}
main {
  margin: 0 auto;
  max-width: 1180px;
  padding: 32px 20px 48px;
}
h1 {
  font-size: 30px;
  letter-spacing: 0;
  margin: 0 0 16px;
}
h2 {
  border-bottom: 1px solid #d7dce2;
  font-size: 20px;
  letter-spacing: 0;
  margin: 28px 0 12px;
  padding-bottom: 8px;
}
.notice {
  background: #ffffff;
  border: 1px solid #d7dce2;
  border-left: 5px solid #315c8a;
  border-radius: 6px;
  padding: 12px 16px;
}
.summary-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
}
.metric {
  background: #ffffff;
  border: 1px solid #d7dce2;
  border-radius: 6px;
  padding: 10px 12px;
}
.metric span {
  color: #5b6773;
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
}
table {
  background: #ffffff;
  border-collapse: collapse;
  border: 1px solid #d7dce2;
  font-size: 13px;
  width: 100%;
}
th, td {
  border-bottom: 1px solid #e5e8ec;
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #eef2f6;
}
.table-wrap {
  overflow-x: auto;
}
ul {
  background: #ffffff;
  border: 1px solid #d7dce2;
  border-radius: 6px;
  margin: 0;
  padding: 14px 18px 14px 32px;
}
""".strip()


def _summary_section(summary: DashboardStabilityIndicatorsSummary | None) -> str:
    if summary is None:
        return "<section><h2>Snapshot Context</h2><p>No summary was produced.</p></section>"
    metrics = [
        ("Symbol", summary.symbol),
        ("H4 Timeframe", summary.h4_timeframe),
        ("D1 Timeframe", summary.d1_timeframe),
        ("Stability Dimensions", summary.stability_dimension_count),
        ("Reference Cards", summary.reference_card_count),
        ("Stable Indicators", summary.stable_evidence_indicator_count),
        ("Partial Indicators", summary.partial_evidence_indicator_count),
        ("Warning Indicators", summary.warning_evidence_indicator_count),
        ("Scope Safety", summary.scope_safety_class),
        ("Readiness Class", summary.dashboard_stability_readiness_class),
        ("Readiness Flag", summary.dashboard_stability_readiness_flag),
        ("Recommended Follow-Up", summary.recommended_follow_up),
    ]
    cards = "\n".join(
        f'<div class="metric"><span>{escape(str(label))}</span>{escape(str(value))}</div>'
        for label, value in metrics
    )
    return f'<section><h2>Snapshot Context</h2><div class="summary-grid">{cards}</div></section>'


def _table_section(title: str, frame: pd.DataFrame) -> str:
    if frame.empty:
        return f"<section><h2>{escape(title)}</h2><p>No rows were produced.</p></section>"
    header = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(f"<td>{escape(str(row.get(column, '')))}</td>" for column in frame.columns)
        rows.append(f"<tr>{cells}</tr>")
    return (
        f"<section><h2>{escape(title)}</h2>"
        f'<div class="table-wrap"><table><thead><tr>{header}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div></section>"
    )


def _list_section(title: str, items: list[str]) -> str:
    rows = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f"<section><h2>{escape(title)}</h2><ul>{rows}</ul></section>"
