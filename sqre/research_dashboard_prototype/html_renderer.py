"""Static HTML renderer for the SQRE Research Dashboard Prototype."""

from __future__ import annotations

from html import escape

import pandas as pd

from sqre.research_dashboard_prototype.findings import limitation_lines, scope_statements
from sqre.research_dashboard_prototype.models import ResearchDashboardPrototypeResult


def render_html(result: ResearchDashboardPrototypeResult, title: str) -> str:
    summary = result.summary
    readiness = summary.dashboard_readiness_flag if summary else "INPUT_COMPLETENESS_REVIEW_REQUIRED"
    html = [
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
        "<p class=\"warning\">Research-only prototype. This is not live market data unless explicitly connected in a later phase.</p>",
        f"<p class=\"readiness\">Readiness flag: <strong>{escape(readiness)}</strong></p>",
        _section("Snapshot Context", _table(result.snapshot_panel)),
        _section("Evidence Summary", _table(result.evidence_panel)),
        _section("Historical Reference Cards", _cards(result.reference_cards)),
        _section("Fallback Trace", _table(result.fallback_panel)),
        _section("Diagnostics", _table(result.diagnostic_panel)),
        _section("Limitations", _list(limitation_lines())),
        _section("Scope Statements", _list(scope_statements())),
        "</main>",
        "</body>",
        "</html>",
    ]
    return "\n".join(html) + "\n"


def _section(title: str, body: str) -> str:
    return f"<section><h2>{escape(title)}</h2>{body}</section>"


def _table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "<p>No rows available.</p>"
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    body_rows = []
    for _, row in frame.head(25).iterrows():
        cells = "".join(f"<td>{escape(str(row.get(column, '')))}</td>" for column in frame.columns)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<div class=\"table-wrap\"><table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"


def _cards(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "<p>No reference cards available.</p>"
    cards = []
    for _, row in frame.iterrows():
        cards.append(
            "<article class=\"card\">"
            f"<h3>{escape(str(row.get('Reference_Card_ID', 'Reference Card')))}</h3>"
            f"<p><strong>Query:</strong> {escape(str(row.get('Snapshot_Query_ID', '')))}</p>"
            f"<p><strong>Reference:</strong> {escape(str(row.get('Matched_Research_Reference_ID', '')))}</p>"
            f"<p><strong>Match:</strong> {escape(str(row.get('Snapshot_Query_Match_Level', '')))}</p>"
            f"<p><strong>Evidence:</strong> {escape(str(row.get('Snapshot_Evidence_Class', '')))}</p>"
            f"<p><strong>Horizon:</strong> {escape(str(row.get('Matched_Forward_Horizon_H4_Candles', '')))}</p>"
            "</article>"
        )
    return f"<div class=\"cards\">{''.join(cards)}</div>"


def _list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def _css() -> str:
    return """
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f2933; background: #f5f7fa; }
main { max-width: 1180px; margin: 0 auto; padding: 32px 20px; }
h1 { margin: 0 0 10px; font-size: 32px; }
h2 { margin-top: 28px; border-bottom: 1px solid #d8dee8; padding-bottom: 8px; }
.warning { background: #fff7d6; border-left: 4px solid #b7791f; padding: 12px 14px; }
.readiness { background: #e8f3ff; border-left: 4px solid #2f80ed; padding: 12px 14px; }
section { background: #ffffff; border: 1px solid #d8dee8; margin-top: 18px; padding: 18px; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
th, td { border: 1px solid #d8dee8; padding: 8px; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.card { border: 1px solid #d8dee8; padding: 12px; background: #fbfcfe; }
.card h3 { margin-top: 0; font-size: 16px; }
"""
