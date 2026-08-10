"""Render a refined static HTML dashboard for manual research review."""

from __future__ import annotations

from html import escape

import pandas as pd

from sqre.manual_research_dashboard_review.models import ManualResearchDashboardReviewResult
from sqre.manual_research_dashboard_review.usability_findings import limitation_lines, scope_statements


def render_refined_html(result: ManualResearchDashboardReviewResult, title: str) -> str:
    summary = result.summary
    readiness = summary.dashboard_usability_readiness_flag if summary else "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            f"<title>{escape(title)}</title>",
            "<style>",
            _css(),
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            f"<h1>{escape(title)}</h1>",
            _warning(),
            _section("Snapshot Context", _labeled_snapshot(result.frames.get("prototype_snapshot_panel", pd.DataFrame()))),
            _section("Readiness and Coverage", _readiness(result)),
            _section("Evidence Summary", _table(result.frames.get("prototype_evidence_panel", pd.DataFrame()), 10)),
            _section("Historical Reference Cards", _cards(result.frames.get("prototype_reference_cards", pd.DataFrame()))),
            _section("Fallback Trace", _table(result.frames.get("prototype_fallback_panel", pd.DataFrame()), 15)),
            _section("Diagnostics", _table(result.panel_readability, 15)),
            _section("Limitations", _list(limitation_lines())),
            _section("Scope Statements", _list(scope_statements())),
            f"<p class=\"readiness\">Review readiness flag: <strong>{escape(readiness)}</strong></p>",
            "</main>",
            "</body>",
            "</html>",
        ]
    ) + "\n"


def _warning() -> str:
    return (
        "<section class=\"warning\"><h2>Research-Only Warning</h2>"
        "<p>This dashboard summarizes local research outputs only. It is not live market data unless explicitly connected in a later phase.</p>"
        "</section>"
    )


def _section(title: str, body: str) -> str:
    return f"<section><h2>{escape(title)}</h2>{body}</section>"


def _labeled_snapshot(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "<p>No snapshot context rows available.</p>"
    row = frame.iloc[0]
    labels = {
        "Snapshot source": ["Snapshot_Source"],
        "Coverage ratio": ["Snapshot_Reference_Coverage_Ratio"],
        "Evidence class": ["Snapshot_Evidence_Class"],
        "Match level": ["Primary_Snapshot_Query_Match_Level", "Snapshot_Query_Match_Level"],
        "Reference tier": ["Matched_Reference_Tier"],
        "Sample size": ["Matched_Outcome_Sample_Size"],
        "Dispersion": ["Matched_Outcome_Dispersion_Pips"],
        "Horizon": ["Primary_Snapshot_Horizon", "Matched_Forward_Horizon_H4_Candles"],
    }
    items = []
    for label, aliases in labels.items():
        items.append(f"<dt>{escape(label)}</dt><dd>{escape(str(_first(row, aliases)))}</dd>")
    return "<dl class=\"snapshot\">" + "".join(items) + "</dl>"


def _readiness(result: ManualResearchDashboardReviewResult) -> str:
    summary = result.summary
    if summary is None:
        return "<p>Readiness assessment is unavailable.</p>"
    coverage = _coverage_ratio(result.frames.get("prototype_summary", pd.DataFrame()))
    return (
        "<dl class=\"snapshot\">"
        f"<dt>Coverage ratio</dt><dd>{escape(str(coverage))}</dd>"
        f"<dt>Usability readiness class</dt><dd>{escape(str(summary.dashboard_usability_readiness_class))}</dd>"
        f"<dt>Usability readiness flag</dt><dd>{escape(str(summary.dashboard_usability_readiness_flag))}</dd>"
        f"<dt>Follow-up</dt><dd>{escape(str(summary.recommended_follow_up))}</dd>"
        "</dl>"
    )


def _cards(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "<p>No historical reference cards available.</p>"
    cards = []
    for _, row in frame.head(10).iterrows():
        cards.append(
            "<article class=\"card\">"
            f"<h3>{escape(str(row.get('Reference_Card_ID', 'Reference Card')))}</h3>"
            f"<p><strong>Match level:</strong> {escape(str(row.get('Snapshot_Query_Match_Level', '')))}</p>"
            f"<p><strong>Reference tier:</strong> {escape(str(row.get('Matched_Reference_Tier', '')))}</p>"
            f"<p><strong>Sample size:</strong> {escape(str(row.get('Matched_Outcome_Sample_Size', '')))}</p>"
            f"<p><strong>Dispersion:</strong> {escape(str(row.get('Matched_Outcome_Dispersion_Pips', '')))}</p>"
            f"<p><strong>Horizon:</strong> {escape(str(row.get('Matched_Forward_Horizon_H4_Candles', '')))}</p>"
            f"<p><strong>Evidence class:</strong> {escape(str(row.get('Snapshot_Evidence_Class', '')))}</p>"
            "</article>"
        )
    return f"<div class=\"cards\">{''.join(cards)}</div>"


def _table(frame: pd.DataFrame, limit: int) -> str:
    if frame.empty:
        return "<p>No rows available.</p>"
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    body_rows = []
    for _, row in frame.head(limit).iterrows():
        cells = "".join(f"<td>{escape(str(row.get(column, '')))}</td>" for column in frame.columns)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<div class=\"table-wrap\"><table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"


def _list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def _first(row: pd.Series, aliases: list[str]) -> object:
    for alias in aliases:
        if alias in row.index and pd.notna(row.get(alias)):
            return row.get(alias)
    return ""


def _coverage_ratio(frame: pd.DataFrame) -> object:
    if frame.empty:
        return ""
    return _first(frame.iloc[0], ["Snapshot_Reference_Coverage_Ratio"])


def _css() -> str:
    return """
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f2933; background: #f4f6f8; }
main { max-width: 1180px; margin: 0 auto; padding: 30px 18px; }
h1 { margin: 0 0 12px; font-size: 30px; }
h2 { margin: 0 0 12px; font-size: 20px; }
section { background: #fff; border: 1px solid #d9e1ea; margin: 16px 0; padding: 18px; }
.warning { border-left: 5px solid #9a6700; background: #fff8dc; }
.readiness { background: #e8f4ff; border-left: 5px solid #2563eb; padding: 12px; }
.snapshot { display: grid; grid-template-columns: minmax(170px, 260px) 1fr; gap: 8px 14px; }
dt { font-weight: 700; }
dd { margin: 0; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { border: 1px solid #d9e1ea; padding: 8px; vertical-align: top; text-align: left; }
th { background: #eef3f8; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; }
.card { border: 1px solid #d9e1ea; background: #fbfcfd; padding: 12px; }
.card h3 { margin: 0 0 8px; font-size: 16px; }
"""
